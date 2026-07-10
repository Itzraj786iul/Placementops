import type { Department } from "@/features/student-onboarding/types";
import type {
  AcademicInformation,
  PersonalInformation,
  StudentProfile,
} from "@/features/student-onboarding/types";
import type {
  EligibilityCheck,
  EligibilityRule,
} from "@/features/student-opportunities/types";

export function checkEligibility(
  rule: EligibilityRule | undefined,
  profile: StudentProfile | undefined,
  academic: AcademicInformation | undefined,
  personal: PersonalInformation | undefined,
  departments: Department[],
): EligibilityCheck {
  if (!rule || !profile) {
    return {
      eligible: false,
      reasons: ["Complete your student profile to check eligibility."],
    };
  }

  const reasons: string[] = [];

  if (rule.minimum_cgpa != null && academic) {
    const cgpa = parseFloat(academic.current_cgpa);
    const min = parseFloat(rule.minimum_cgpa);
    if (!Number.isNaN(cgpa) && !Number.isNaN(min) && cgpa < min) {
      reasons.push(`Minimum CGPA required is ${min}. Your CGPA is ${cgpa}.`);
    }
  } else if (rule.minimum_cgpa != null && !academic) {
    reasons.push(
      "Academic information is required to verify CGPA eligibility.",
    );
  }

  if (rule.allowed_departments?.length) {
    const allowed = new Set(rule.allowed_departments.map(String));
    if (!allowed.has(profile.department_id)) {
      const dept = departments.find((d) => d.id === profile.department_id);
      reasons.push(
        `This opportunity is limited to specific departments. Your department (${dept?.name ?? "Unknown"}) is not listed.`,
      );
    }
  }

  if (rule.allowed_graduation_years?.length) {
    if (!rule.allowed_graduation_years.includes(profile.graduation_year)) {
      reasons.push(
        `Graduation year ${profile.graduation_year} is not eligible. Allowed: ${rule.allowed_graduation_years.join(", ")}.`,
      );
    }
  }

  if (rule.maximum_active_backlogs != null && academic) {
    if (academic.active_backlogs > rule.maximum_active_backlogs) {
      reasons.push(
        `Maximum active backlogs allowed is ${rule.maximum_active_backlogs}. You have ${academic.active_backlogs}.`,
      );
    }
  }

  if (rule.gender_restriction && personal) {
    if (
      personal.gender.toLowerCase() !== rule.gender_restriction.toLowerCase()
    ) {
      reasons.push(`Gender restriction: ${rule.gender_restriction} only.`);
    }
  }

  if (
    !rule.allow_backlog_history &&
    academic &&
    academic.total_history_backlogs > 0
  ) {
    reasons.push("Backlog history is not permitted for this opportunity.");
  }

  return { eligible: reasons.length === 0, reasons };
}
