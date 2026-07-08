import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MedVitals API")

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
    provider_name: str


# 2. MOCK DATA STORE (In-Memory Database)
MOCK_PATIENTS = {
    "1": FHIRPatient(
        id="1",
        resourceType="Patient",
        name=[HumanName(given=["Jane", "Marie"], family="Doe")],
        gender="female",
        birthDate="1990-05-12"
    ),
    "2": FHIRPatient(
        id="2",
        resourceType="Patient",
        name=[HumanName(given=["John", "Robert"], family="Smith")],
        gender="male",
        birthDate="1985-11-23"
    )
}

MOCK_VITALS = {
    "1": [
        {
            "resourceType": "Observation",
            "id": "v1",
            "status": "final",
            "code": {
                "text": "Heart Rate",
                "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
            },
            "valueQuantity": {
                "value": 72,
                "unit": "bpm"
            },
            "effectiveDateTime": "2026-07-08T10:00:00Z"
        },
        {
            "resourceType": "Observation",
            "id": "v2",
            "status": "final",
            "code": {
                "text": "Blood Pressure",
                "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]
            },
            "valueQuantity": {
                "value": 120, # In a full production app this would be a nested component, but keeping it clean for our MVP value quantity
                "unit": "mmHg"
            },
            "effectiveDateTime": "2026-07-08T10:00:00Z"
        }
    ],
    "2": [
        {
            "resourceType": "Observation",
            "id": "v3",
            "status": "final",
            "code": {
                "text": "Heart Rate",
                "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
            },
            "valueQuantity": {
                "value": 85,
                "unit": "bpm"
            },
            "effectiveDateTime": "2026-07-08T09:30:00Z"
        }
    ]
}


# 3. API ENDPOINTS
@app.get("/api/patients", response_model=List[FHIRPatient])
def get_all_patients():
    """Returns a list of all patients in the system."""
    return list(MOCK_PATIENTS.values())

@app.get("/api/patients/{patient_id}/vitals", response_model=List[VitalObservation])
def get_patient_vitals(patient_id: str):
    """Returns the vital signs for a specific patient ID."""
    if patient_id not in MOCK_VITALS:
        raise HTTPException(status_code=404, detail="Patient vital records not found")
    print(f"Fetching vitals for patient ID: {patient_id}")
    return MOCK_VITALS[patient_id]

@app.post("/api/providers/verify")
async def verify_provider_credential(payload: VerificationRequest):
    """Simulates an asynchronous background check on a doctor's license."""
    # Simulate network latency of hitting a government state board API
    await asyncio.sleep(2) 
    
    # Simple mock check rule for the MVP
    if len(payload.npi_number) != 10 or not payload.npi_number.isdigit():
        return {
            "status": "denied",
            "reason": "Invalid NPI formatting. Must be exactly 10 digits.",
            "verified": False
        }
    
    return {
        "status": "verified",
        "verified": True,
        "assigned_credentials": f"MD-Active-{payload.npi_number[:4]}"
    }