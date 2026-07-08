export interface HumanName {
  given: string[];
  family: string;
}

export interface FHIRPatient {
  resourceType: string;
  id: string;
  name: HumanName[];
  gender: string;
  birthDate: string;
}

export interface VitalObservation {
  resourceType: string;
  id: string;
  code: string;
  value: string;
  effectiveDateTime: string;
}