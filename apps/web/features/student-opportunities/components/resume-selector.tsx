"use client";

import { Select } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import type { Resume } from "@/features/student-onboarding/types";

type ResumeSelectorProps = {
  resumes: Resume[];
  value: string;
  onChange: (resumeId: string) => void;
  disabled?: boolean;
};

export function ResumeSelector({
  resumes,
  value,
  onChange,
  disabled = false,
}: ResumeSelectorProps) {
  const activeResumes = resumes.filter((r) => r.is_active);

  if (activeResumes.length === 0) {
    return (
      <p className="text-destructive text-sm">
        No active resume found. Set an active resume in your student profile
        first.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="resume-select">Select resume</Label>
      <Select
        id="resume-select"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Select resume for application"
      >
        <option value="">Choose a resume</option>
        {activeResumes.map((resume) => (
          <option key={resume.id} value={resume.id}>
            {resume.name} (v{resume.version})
          </option>
        ))}
      </Select>
    </div>
  );
}
