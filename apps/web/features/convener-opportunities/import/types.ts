export type MatchField = "ROLL_NUMBER" | "REGISTRATION_NUMBER" | "EMAIL";

export type ImportableStatus =
  | "SHORTLISTED"
  | "ASSESSMENT"
  | "INTERVIEW"
  | "SELECTED"
  | "OFFER_RELEASED"
  | "REJECTED";

export type RowMatchStatus = "MATCHED" | "UNMATCHED" | "DUPLICATE" | "INVALID";

export type ImportStatus = "PREVIEW" | "CONFIRMED";

export type ImportRowPreview = {
  id: string;
  row_number: number;
  raw_identifier: string;
  match_status: RowMatchStatus;
  application_id: string | null;
  student_name: string | null;
  current_status: string | null;
  message: string | null;
};

export type ImportPreviewResponse = {
  id: string;
  hiring_opportunity_id: string;
  imported_by: string;
  filename: string;
  match_field: MatchField;
  target_status: ImportableStatus;
  status: ImportStatus;
  total_rows: number;
  matched_rows: number;
  unmatched_rows: number;
  duplicate_rows: number;
  invalid_rows: number;
  rows_updated: number | null;
  rows_skipped: number | null;
  imported_at: string;
  confirmed_at: string | null;
  rows: ImportRowPreview[];
};

export type ImportConfirmResponse = {
  id: string;
  status: ImportStatus;
  target_status: ImportableStatus;
  imported_by: string;
  imported_at: string;
  confirmed_at: string | null;
  rows_updated: number;
  rows_skipped: number;
  matched_rows: number;
  unmatched_rows: number;
  duplicate_rows: number;
  invalid_rows: number;
};

export const MATCH_FIELD_OPTIONS: { value: MatchField; label: string }[] = [
  { value: "ROLL_NUMBER", label: "Roll number" },
  { value: "REGISTRATION_NUMBER", label: "Registration number" },
  { value: "EMAIL", label: "Email" },
];

export const IMPORTABLE_STATUS_OPTIONS: ImportableStatus[] = [
  "SHORTLISTED",
  "ASSESSMENT",
  "INTERVIEW",
  "SELECTED",
  "OFFER_RELEASED",
  "REJECTED",
];

export const ROW_MATCH_STATUS_LABELS: Record<RowMatchStatus, string> = {
  MATCHED: "Matched",
  UNMATCHED: "Unmatched",
  DUPLICATE: "Duplicate",
  INVALID: "Invalid",
};
