# NO IMPORTS AT THE TOP

MOCK_PATIENTS = {
    "1": {
        "id": "1",
        "resourceType": "Patient",
        "name": [{"given": ["Jane", "Marie"], "family": "Doe"}],
        "gender": "female",
        "birthDate": "1990-05-12"
    },
    "2": {
        "id": "2",
        "resourceType": "Patient",
        "name": [{"given": ["John", "Robert"], "family": "Smith"}],
        "gender": "male",
        "birthDate": "1985-11-23"
    },
    "3": {
        "id": "3",
        "resourceType": "Patient",
        "name": [{"given": ["Clara", "Oswald"], "family": "Ondos"}],
        "gender": "female",
        "birthDate": "1994-03-14"
    },
    "4": {
        "id": "4",
        "resourceType": "Patient",
        "name": [{"given": ["Bruce", "Wayne"], "family": "Thomas"}],
        "gender": "male",
        "birthDate": "1979-02-19"
    }
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
            "valueQuantity": {"value": 72, "unit": "bpm"},
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
            "valueQuantity": {"value": 122, "unit": "mmHg"},
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
            "valueQuantity": {"value": 89, "unit": "bpm"},
            "effectiveDateTime": "2026-07-08T09:30:00Z"
        }
    ],
    "3": [
        {
            "resourceType": "Observation",
            "id": "v4",
            "status": "final",
            "code": {
                "text": "Heart Rate",
                "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
            },
            "valueQuantity": {"value": 61, "unit": "bpm"},
            "effectiveDateTime": "2026-07-08T08:15:00Z"
        },
        {
            "resourceType": "Observation",
            "id": "v5",
            "status": "final",
            "code": {
                "text": "Blood Pressure",
                "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]
            },
            "valueQuantity": {"value": 115, "unit": "mmHg"},
            "effectiveDateTime": "2026-07-08T08:15:00Z"
        }
    ],
    "4": [
        {
            "resourceType": "Observation",
            "id": "v6",
            "status": "final",
            "code": {
                "text": "Heart Rate",
                "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
            },
            "valueQuantity": {"value": 105, "unit": "bpm"},
            "effectiveDateTime": "2026-07-08T11:45:00Z"
        },
        {
            "resourceType": "Observation",
            "id": "v7",
            "status": "final",
            "code": {
                "text": "Blood Pressure",
                "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]
            },
            "valueQuantity": {"value": 145, "unit": "mmHg"},
            "effectiveDateTime": "2026-07-08T11:45:00Z"
        }
    ]
}