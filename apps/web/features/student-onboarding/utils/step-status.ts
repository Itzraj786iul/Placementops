import type {
  StepperItem,
  StepState,
} from "@/features/student-onboarding/components/onboarding-stepper";
import type { OnboardingStepId } from "@/features/student-onboarding/constants";
import {
  ONBOARDING_STEPS,
  REQUIRED_DOCUMENT_TYPES,
} from "@/features/student-onboarding/constants";
import type {
  AcademicInformation,
  EducationRecord,
  PersonalInformation,
  Project,
  Resume,
  Skill,
  StudentDocument,
  Verification,
} from "@/features/student-onboarding/types";

export type SectionData = {
  personal?: PersonalInformation | null;
  academic?: AcademicInformation | null;
  education: EducationRecord[];
  resumes: Resume[];
  documents: StudentDocument[];
  skills: Skill[];
  projects: Project[];
  verification?: Verification | null;
};

function isPersonalComplete(data: SectionData): boolean {
  return Boolean(data.personal);
}

function isAcademicComplete(data: SectionData): boolean {
  return Boolean(data.academic);
}

function isEducationComplete(data: SectionData): boolean {
  return data.education.length > 0;
}

function isResumeComplete(data: SectionData): boolean {
  return data.resumes.length > 0;
}

function isDocumentsComplete(data: SectionData): boolean {
  const uploaded = new Set(data.documents.map((d) => d.document_type));
  return REQUIRED_DOCUMENT_TYPES.every((type) => uploaded.has(type));
}

function isSkillsComplete(data: SectionData): boolean {
  return data.skills.length > 0;
}

function isProjectsComplete(data: SectionData): boolean {
  return data.projects.length > 0;
}

const COMPLETION_CHECKS: Record<
  OnboardingStepId,
  (data: SectionData) => boolean
> = {
  personal: isPersonalComplete,
  academic: isAcademicComplete,
  education: isEducationComplete,
  resume: isResumeComplete,
  documents: isDocumentsComplete,
  skills: isSkillsComplete,
  projects: isProjectsComplete,
  review: () => false,
};

const STARTED_CHECKS: Record<OnboardingStepId, (data: SectionData) => boolean> =
  {
    personal: (data) => Boolean(data.personal),
    academic: (data) => Boolean(data.academic),
    education: (data) => data.education.length > 0,
    resume: (data) => data.resumes.length > 0,
    documents: (data) => data.documents.length > 0,
    skills: (data) => data.skills.length > 0,
    projects: (data) => data.projects.length > 0,
    review: () => false,
  };

const REJECTION_MAP: Partial<Record<OnboardingStepId, keyof Verification>> = {
  personal: "personal_status",
  academic: "academic_status",
  resume: "resume_status",
  documents: "documents_status",
};

export function getSectionStatus(
  stepId: OnboardingStepId,
  data: SectionData,
): "complete" | "incomplete" | "not_started" {
  if (stepId === "review") return "not_started";
  if (COMPLETION_CHECKS[stepId](data)) return "complete";
  if (STARTED_CHECKS[stepId](data)) return "incomplete";
  return "not_started";
}

export function getFirstIncompleteStep(data: SectionData): OnboardingStepId {
  for (const step of ONBOARDING_STEPS) {
    if (step.id === "review") continue;
    if (!COMPLETION_CHECKS[step.id](data)) return step.id;
  }
  return "review";
}

export function buildStepperItems(
  currentStep: OnboardingStepId,
  data: SectionData,
): StepperItem[] {
  const firstIncomplete = getFirstIncompleteStep(data);

  return ONBOARDING_STEPS.map((step) => {
    let state: StepState = "current";
    const sectionStatus = getSectionStatus(step.id, data);

    const rejectionField = REJECTION_MAP[step.id];
    if (rejectionField && data.verification?.[rejectionField] === "REJECTED") {
      state = "rejected";
    } else if (step.id === currentStep) {
      state = sectionStatus === "complete" ? "completed" : "current";
    } else if (sectionStatus === "complete") {
      state = "completed";
    } else if (
      step.order > ONBOARDING_STEPS.find((s) => s.id === firstIncomplete)!.order
    ) {
      state = "locked";
    } else if (sectionStatus === "incomplete") {
      state = "incomplete";
    } else {
      state = "not_started";
    }

    return { id: step.id, label: step.label, state };
  });
}

export function getIncompleteSections(data: SectionData): string[] {
  return ONBOARDING_STEPS.filter(
    (step) => step.id !== "review" && !COMPLETION_CHECKS[step.id](data),
  ).map((step) => step.label);
}

export function missingForStep(
  stepId: OnboardingStepId,
  missing: { code: string; label: string; step: string }[],
): string[] {
  return missing
    .filter((item) => item.step === stepId)
    .map((item) => item.label);
}
