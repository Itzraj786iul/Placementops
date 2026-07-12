"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchAcademicInfo,
  fetchDepartments,
  fetchDocuments,
  fetchEducationHistory,
  fetchMyProfile,
  fetchPersonalInfo,
  fetchProjects,
  fetchResumes,
  fetchSkills,
  fetchVerification,
} from "@/features/student-onboarding/api/student-client";
import { ApiError } from "@/lib/api-client";

export type StudentSectionKey =
  | "personal"
  | "academic"
  | "education"
  | "resumes"
  | "documents"
  | "skills"
  | "projects"
  | "verification";

export const studentQueryKeys = {
  profile: ["student", "profile"] as const,
  departments: ["student", "departments"] as const,
  personal: (id: string) => ["student", "personal", id] as const,
  academic: (id: string) => ["student", "academic", id] as const,
  education: (id: string) => ["student", "education", id] as const,
  resumes: (id: string) => ["student", "resumes", id] as const,
  documents: (id: string) => ["student", "documents", id] as const,
  skills: (id: string) => ["student", "skills", id] as const,
  projects: (id: string) => ["student", "projects", id] as const,
  verification: (id: string) => ["student", "verification", id] as const,
};

const SECTION_KEY_FN: Record<
  StudentSectionKey,
  (id: string) => readonly unknown[]
> = {
  personal: studentQueryKeys.personal,
  academic: studentQueryKeys.academic,
  education: studentQueryKeys.education,
  resumes: studentQueryKeys.resumes,
  documents: studentQueryKeys.documents,
  skills: studentQueryKeys.skills,
  projects: studentQueryKeys.projects,
  verification: studentQueryKeys.verification,
};

export function useStudentProfile() {
  return useQuery({
    queryKey: studentQueryKeys.profile,
    queryFn: fetchMyProfile,
    retry: (count, error) => {
      if (error instanceof ApiError && error.statusCode === 404) return false;
      return count < 2;
    },
  });
}

export function useDepartments() {
  return useQuery({
    queryKey: studentQueryKeys.departments,
    queryFn: fetchDepartments,
  });
}

export function useStudentOnboardingData(profileId: string | undefined) {
  const personal = useQuery({
    queryKey: studentQueryKeys.personal(profileId ?? ""),
    queryFn: () => fetchPersonalInfo(profileId!),
    enabled: Boolean(profileId),
    retry: false,
  });
  const academic = useQuery({
    queryKey: studentQueryKeys.academic(profileId ?? ""),
    queryFn: () => fetchAcademicInfo(profileId!),
    enabled: Boolean(profileId),
    retry: false,
  });
  const education = useQuery({
    queryKey: studentQueryKeys.education(profileId ?? ""),
    queryFn: () => fetchEducationHistory(profileId!),
    enabled: Boolean(profileId),
  });
  const resumes = useQuery({
    queryKey: studentQueryKeys.resumes(profileId ?? ""),
    queryFn: () => fetchResumes(profileId!),
    enabled: Boolean(profileId),
  });
  const documents = useQuery({
    queryKey: studentQueryKeys.documents(profileId ?? ""),
    queryFn: () => fetchDocuments(profileId!),
    enabled: Boolean(profileId),
  });
  const skills = useQuery({
    queryKey: studentQueryKeys.skills(profileId ?? ""),
    queryFn: () => fetchSkills(profileId!),
    enabled: Boolean(profileId),
  });
  const projects = useQuery({
    queryKey: studentQueryKeys.projects(profileId ?? ""),
    queryFn: () => fetchProjects(profileId!),
    enabled: Boolean(profileId),
  });
  const verification = useQuery({
    queryKey: studentQueryKeys.verification(profileId ?? ""),
    queryFn: () => fetchVerification(profileId!),
    enabled: Boolean(profileId),
    retry: false,
  });

  return {
    personal,
    academic,
    education,
    resumes,
    documents,
    skills,
    projects,
    verification,
  };
}

export function useInvalidateStudentQueries() {
  const queryClient = useQueryClient();

  return {
    invalidateProfile: () =>
      queryClient.invalidateQueries({ queryKey: studentQueryKeys.profile }),
    /** Refresh completion + one or more section caches only. */
    invalidateSections: (profileId: string, sections: StudentSectionKey[]) => {
      void queryClient.invalidateQueries({
        queryKey: studentQueryKeys.profile,
      });
      for (const section of sections) {
        void queryClient.invalidateQueries({
          queryKey: SECTION_KEY_FN[section](profileId),
        });
      }
    },
    /** @deprecated Prefer invalidateSections for targeted refreshes. */
    invalidateAll: (profileId: string) => {
      void queryClient.invalidateQueries({
        queryKey: studentQueryKeys.profile,
      });
      for (const section of Object.keys(
        SECTION_KEY_FN,
      ) as StudentSectionKey[]) {
        void queryClient.invalidateQueries({
          queryKey: SECTION_KEY_FN[section](profileId),
        });
      }
    },
  };
}
