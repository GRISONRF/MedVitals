# MedVitals Provider Operations & Clinical Analytics Dashboard

A full-stack medical operations platform engineered to demonstrate enterprise-grade health-tech architectures, distributed data pipelines, and real-time automated compliance engine workflows using **FastAPI (Python 3.12)** and **React (TypeScript / Tailwind CSS)**.

---

## 🚀 Key Architectural Features & Health-Tech Concepts

### 1. Real-Time Clinical Decision Support (CDS Hooks Standard)
* **The Concept:** Implements a decoupled micro-rules engine mirroring the HL7 federal **CDS Hooks** specification. 
* **How it Works:** When an operator views a patient chart, a hook event is transmitted to the backend validation module. The engine evaluates live metrics against strict clinical baselines (e.g., Tachycardia or Hypertension thresholds) and returns a collection of structured, actionable clinical alert **"Cards"** directly into the user interface.

### 2. High-Volume Asynchronous Bulk Data Pipelines ($export)
* **The Concept:** Implements the official **FHIR Bulk Data Access ($export)** protocol using an **Asynchronous Job Queue / State Machine pattern**.
* **How it Works:** Compiling large hospital registries takes high computational overhead. To prevent server thread exhaustion or connection timeouts, the `/api/patients/$export` endpoint handles requests asynchronously. The backend offloads the streaming process to a dedicated worker thread via FastAPI `BackgroundTasks` and instantly issues an HTTP **`202 Accepted`** claim ticket token. The frontend utilizes a dynamic polling clock to safely monitor progress until a streamable, memory-efficient **`.ndjson` (Newline Delimited JSON)** file download link is exposed.

### 3. Live Federal Registry Orchestration (CMS NPPES API)
* **The Concept:** Automates credential checking by integrating your proxy tier directly with the live, production-grade **National Plan and Provider Enumeration System (NPPES)** registry run by the US Centers for Medicare & Medicaid Services (CMS).
* **How it Works:** The application consumes a 10-digit National Provider Identifier (NPI), bypasses automated scraping/TLS security boundaries enforced by government firewalls via modern connection masquerading techniques, extracts nested provider attributes dynamically, and yields verified clinician taxonomic metadata.

### 4. Semantic Healthcare Interoperability (HL7 FHIR Profiles)
* **The Concept:** Avoids localized data modeling variations by mapping all in-memory database layouts strictly to the global standard **HL7 FHIR (Fast Healthcare Interoperability Resources)** schema.
* **How it Works:** Patient identifiers are serialized as standardized `Patient` structures, and vital signs are mapped into strictly typed, nested `Observation` object models containing standard LOINC system coding detail schemas.

---

## 📷 App Walkthrough & Features

![Dashboard Main View](https://raw.githubusercontent.com/GRISONRF/MedVitals/main/images/images/full.png)

### 1. Patient Clinical Tracker (HL7 FHIR Format) & CDS Hooks
When a patient profile is selected, the application requests the raw FHIR `Observation` payload. Simultaneously, the **CDS Hooks rules engine** runs on the backend. If metrics cross critical thresholds (such as high heart rate or blood pressure), color-coded alert panels are dynamically injected with embedded action scripts.

![Clinical Tracker](https://github.com/GRISONRF/MedVitals/blob/images/images/heart-blood.png)


### 2. Provider Credentialing Engine (Live CMS NPPES Sync)
Entering a 10-digit National Provider Identifier (NPI) hits the live production federal registry, stripping out server network transport blocks and extracting nested practitioner taxonomy parameters instantly.

![Provider Verification Module](https://github.com/GRISONRF/MedVitals/main/images/images/credentials.png)

### 3. Asynchronous Population $export Pipeline (.ndjson)
Clicking the bulk export initiator dispatches an asynchronous job task. The UI displays state progress values via a long-polling hook routine until a streamable, standardized `.ndjson` bulk file token is generated.

![Bulk Export In Progress](https://github.com/GRISONRF/MedVitals/main/images/images/bulk-export.png)

---

## 🛠️ Technology Stack

* **Backend:** Python 3.12, FastAPI (Asynchronous ASGI Framework), Pydantic v2 (Data Validation & Serialization), Uvicorn.
* **Frontend:** React 18+, TypeScript, Tailwind CSS, Vite.
* **Network Transport Clients:** HTTPX / native OS SChannel wrappers.

---

## 📁 System Architecture & Separation of Concerns

```text
medvitals/
├── backend/
│   ├── main.py          # FastAPI application routing, Pydantic contracts & CDS logic
│   ├── mock_db.py       # Decoupled data store layer (Pure FHIR-compliant payloads)
│   └── .venv/           # Isolated python virtual runtime environment
└── frontend/
    ├── src/
    │   ├── App.tsx      # Main state tracker, polling engine, dashboard interface
    │   └── main.tsx     # Application entrypoint
    ├── package.json
    └── tailwind.config.js

```

---

## 💻 How to Clone and Run Locally

Follow these instructions to clone the repository and run both the FastAPI backend and React frontend services on your local environment.

### 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/medvitals.git](https://github.com/YOUR_GITHUB_USERNAME/medvitals.git)
cd medvitals
```

### 2. Configure and Start the Backend
Open a terminal tab inside the root of the cloned repository folder:

```
# 1. Create a virtual environment inside your project folder
python -m venv .venv

# 2. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 3. Install required production-grade dependencies
pip install fastapi uvicorn pydantic requests httpx

# 4. Boot up the local development web server
uvicorn main:app --reload
```
The API layer will now be listening live for calls on http://127.0.0.1:8000.


### 3. Configure and Start the Frontend
Open a second, separate terminal window or tab and navigate back to your project workspace:
```
# 1. Navigate to the frontend directory containing package.json
cd frontend

# 2. Install package node module dependencies
npm install

# 3. Boot up the Vite local application server
npm run dev
```
Vite will compile your modules and launch your application client interface at http://localhost:5173.

