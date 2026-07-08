export interface FHIRIdentifier {
  use: string;
  system: string;
  value: string;
}

export interface FHIRName {
  use: string;
  family: string;
  given: string[];
}

export interface FHIRPatient {
  resourceType: "Patient";
  id: string;
  active: boolean;
  name: FHIRName[];
  gender: string;
  birthDate: string;
  identifier: FHIRIdentifier[]; // To store things like NPI or Medical Record Numbers
}

export interface VitalObservation {
  resourceType: "Observation";
  id: string;
  status: string;
  code: {
    text: string;
    coding: Array<{ system: string; code: string; display: string }>;
  };
  valueQuantity: {
    value: number;
    unit: string;
  };
  effectiveDateTime: string;
}