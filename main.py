from mock_db import MOCK_PATIENTS, MOCK_VITALS
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import traceback
import uuid
import time
from fastapi import BackgroundTasks

app = FastAPI(title="MedVitals API")

# Global in-memory storage simulating a background job runner tracking state
# In a massive system, this would be Redis or PostgreSQL
EXPORT_JOBS = {}

# CRITICAL FOR PORT 3000 TO TALK TO PORT 8000
# This allows your React frontend to securely request data from this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Vite uses 5173 by default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. DEFINE PYDANTIC SCHEMAS (Matches the HL7 FHIR Standard Structure)
class HumanName(BaseModel):
    given: List[str]
    family: str

class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    name: List[HumanName]
    gender: str
    birthDate: str

class CodingDetail(BaseModel):
    system: str
    code: str
    display: str

class ObservationCode(BaseModel):
    text: str
    coding: List[CodingDetail]

class QuantityModel(BaseModel):
    value: float
    unit: str

# This now perfectly mirrors the nested HL7 FHIR standard
class VitalObservation(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str
    code: ObservationCode       # Nested object instead of a flat string!
    valueQuantity: QuantityModel # New nested model instead of a flat string!
    effectiveDateTime: str

class VerificationRequest(BaseModel):
    npi_number: str

# 3. API ENDPOINTS
@app.get("/api/patients", response_model=List[FHIRPatient])
def get_all_patients():
    """Returns a list of all patients in the system."""
    # FastAPI automatically reads these dictionaries and parses them into FHIRPatient shapes
    return list(MOCK_PATIENTS.values())

@app.get("/api/patients/{patient_id}/vitals", response_model=List[VitalObservation])
def get_patient_vitals(patient_id: str):
    """Returns the vital signs for a specific patient ID."""
    if patient_id not in MOCK_VITALS:
        raise HTTPException(status_code=404, detail="Patient vital records not found")
    print(f"Fetching vitals for patient ID: {patient_id}")
    return MOCK_VITALS[patient_id]


# OLD VERSION THAT SIMULATES A PROVIDER CREDENTIAL VERIFICATION 
# @app.post("/api/providers/verify")
# async def verify_provider_credential(payload: VerificationRequest):
#     """Simulates an asynchronous background check on a doctor's license."""
#     # Simulate network latency of hitting a government state board API
#     await asyncio.sleep(2) 
    
#     # Simple mock check rule for the MVP
#     if len(payload.npi_number) != 10 or not payload.npi_number.isdigit():
#         return {
#             "status": "denied",
#             "reason": "Invalid NPI formatting. Must be exactly 10 digits.",
#             "verified": False
#         }
    
#     return {
#         "status": "verified",
#         "verified": True,
#         "assigned_credentials": f"MD-Active-{payload.npi_number[:4]}"
#     }

@app.post("/api/providers/verify")
async def verify_provider_credential(payload: VerificationRequest):
    """Queries the real US Government NPPES Registry API for provider validation."""

    nppes_url = f"https://npiregistry.cms.hhs.gov/api/?number={payload.npi_number}&enumeration_type=&taxonomy_description=&name_purpose=&first_name=&use_first_name_alias=&last_name=&organization_name=&address_purpose=&city=&state=&postal_code=&country_code=&limit=&skip=&pretty=&version=2.1"


    try:

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(nppes_url, timeout=5.0)

        if response.status_code != 200:
            return {
                "status": "error",
                "verified": False,
                "reason": f"Failed to reach NPPES API. Status code: {response.status_code}"
            }

        data = response.json()
        result_count = data.get("result_count", 0)

        # If the government database returns 0 results, the NPI is fake or invalid:
        if result_count == 0:
            return {
                "status": "denied",
                "verified": False,
                "reason": f"No active medical provider registry found for NPI: {payload.npi_number}"            
            }
        
        return {
            "status": "verified",
            "verified": True,
            "provider_name": f"{data['results'][0]['basic']['first_name']} {data['results'][0]['basic']['last_name']}",
            "assigned_credentials": f"MD-Active-{payload.npi_number[:4]}"
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "status": "error",
            "verified": False,
            "reason": f"Internal system error during processing: {str(e)}"
    }

def simulate_heavy_data_compilation(job_id: str):
    """
    Simulates a background worker thread reading thousands of database records,
    converting them to HL7 FHIR bundles, and writing them to a bulk file.
    """
    # Wait 8 seconds to give time to see the "Processing" state on the UI
    time.sleep(8) 
    
    # Update the job state machine once the file is "ready"
    EXPORT_JOBS[job_id] = {
        "status": "completed",
        "progress": 100,
        "download_url": f"https://npiregistry.cms.hhs.gov/api/?number=1811988041&version=2.1", # Using a stable doctor URL as a dummy file download target
        "generated_at": "2026-07-08T21:00:00Z",
        "file_type": "application/fhir+ndjson"
    }

@app.post("/api/patients/$export", status_code=202)
async def initiate_bulk_export(background_tasks: BackgroundTasks):
    """Kicks off an asynchronous FHIR Bulk Data Export pipeline.
    Returns an immediate HTTP 202 Accepted status string."""

    job_id = str(uuid.uuid4())
    EXPORT_JOBS[job_id] = {"status": "processing", "progress": 25, "download_url": None}

    # FastAPI's built-in BackgroundTasks hands this function off to a separate
    # worker thread so the main execution path doesn't lock up or freeze
    background_tasks.add_task(simulate_heavy_data_compilation, job_id)

    # In a real app, I'd would pass this task to Celery or an external queue worker
    return {
        "status": "Accepted",
        "job_id": job_id,
        "check_status_at": f"/api/jobs/{job_id}"
    }

@app.get("/api/jobs/{job_id}")
def check_export_job_status(job_id: str):
    """
    Polling endpoint allowing clients to inspect the runtime state of a background task.
    """
    if job_id not in EXPORT_JOBS:
        raise HTTPException(status_code=404, detail="Bulk export execution token not found")
        
    return EXPORT_JOBS[job_id]


@app.get("/api/patients/{patient_id}/cds-services")
def evaluate_clinical_rules(patient_id: str):
    """
    Evaluates active FHIR vitals data against automated clinical rules.
    Returns a collection of structured CDS Hooks 'Cards'.
    """

    if patient_id not in MOCK_VITALS:
        return {"cards": []}
    
    cards = []
    patient_vitals = MOCK_VITALS[patient_id]

    # Loop through the patient's observations to check for rule breaches
    for vital in patient_vitals:
        vital_name = vital["code"]["text"]
        vital_value = vital["valueQuantity"]["value"]
        vital_unit = vital["valueQuantity"]["unit"]
        
        # Rule 1: High Heart Rate Check (Tachycardia Alert)
        if vital_name == "Heart Rate" and vital_value > 80:
            cards.append({
                "uuid": str(uuid.uuid4()),
                "summary": "Tachycardia Detected (Elevated Heart Rate)",
                "indicator": "warning",  # Options: info, warning, critical
                "source": {
                    "label": "MedVitals Automated Clinical Engine",
                    "url": "https://example.com/clinical-guidelines"
                },
                "detail": f"The patient's current heart rate is {vital_value} {vital_unit}, which exceeds the standard resting baseline threshold of 80 bpm.",
                "suggestions": [
                    {
                        "label": "Schedule Cardiology Follow-up",
                        "uuid": str(uuid.uuid4())
                    }
                ]
            })
            
        # Rule 2: High Blood Pressure Panel Check (Hypertension Stage 1)
        if vital_name == "Blood Pressure" and vital_value >= 120:
            cards.append({
                "uuid": str(uuid.uuid4()),
                "summary": "Elevated Blood Pressure Warning",
                "indicator": "critical",
                "source": {
                    "label": "AHA Hypertension Guidelines",
                    "url": "https://example.com/aha"
                },
                "detail": f"Systolic reading logged at {vital_value} {vital_unit}. Continuous readings in this range require evaluation for Stage 1 Hypertension.",
                "suggestions": [
                    {
                        "label": "Order 24-Hour BP Monitoring Profile",
                        "uuid": str(uuid.uuid4())
                    }
                ]
            })

    return {"cards": cards}