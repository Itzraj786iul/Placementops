import { apiRequest } from "@/lib/api-client";
import type {
  AcademicInformation,
  Department,
  EducationRecord,
  PersonalInformation,
  Project,
  Resume,
  Skill,
  StudentDocument,
  StudentProfile,
  Verification,
} from "@/features/student-onboarding/types";

export async function fetchDepartments(): Promise<Department[]> {
  return apiRequest<Department[]>("/students/departments");
}

export async function fetchMyProfile(): Promise<StudentProfile> {
  return apiRequest<StudentProfile>("/students/profiles/me");
}

export async function createProfile(payload: {
  department_id: string;
  roll_number: string;
  registration_number: string;
  graduation_year: number;
}): Promise<StudentProfile> {
  return apiRequest<StudentProfile>("/students/profiles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProfile(
  profileId: string,
  payload: Partial<{
    department_id: string;
    roll_number: string;
    registration_number: string;
    graduation_year: number;
    profile_status: string;
  }>,
): Promise<StudentProfile> {
  return apiRequest<StudentProfile>(`/students/profiles/${profileId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchPersonalInfo(
  profileId: string,
): Promise<PersonalInformation> {
  return apiRequest<PersonalInformation>(
    `/students/profiles/${profileId}/personal-information`,
  );
}

export async function savePersonalInfo(
  profileId: string,
  payload: Omit<PersonalInformation, "student_profile_id">,
): Promise<PersonalInformation> {
  return apiRequest<PersonalInformation>(
    `/students/profiles/${profileId}/personal-information`,
    { method: "PUT", body: JSON.stringify(payload) },
  );
}

export async function uploadProfilePhoto(
  profileId: string,
  file: File,
  onProgress: (pct: number) => void = () => undefined,
): Promise<{ photo_url: string }> {
  const { uploadWithProgress, parseUploadError } =
    await import("@/components/ui/file-upload");
  const form = new FormData();
  form.append("file", file);
  const response = await uploadWithProgress(
    `/api/v1/students/profiles/${profileId}/personal-information/photo`,
    form,
    onProgress,
  );
  if (!response.ok) {
    throw new Error(await parseUploadError(response));
  }
  return response.json() as Promise<{ photo_url: string }>;
}

export async function fetchAcademicInfo(
  profileId: string,
): Promise<AcademicInformation> {
  return apiRequest<AcademicInformation>(
    `/students/profiles/${profileId}/academic-information`,
  );
}

export async function saveAcademicInfo(
  profileId: string,
  payload: Omit<AcademicInformation, "student_profile_id">,
): Promise<AcademicInformation> {
  return apiRequest<AcademicInformation>(
    `/students/profiles/${profileId}/academic-information`,
    { method: "PUT", body: JSON.stringify(payload) },
  );
}

export async function fetchEducationHistory(
  profileId: string,
): Promise<EducationRecord[]> {
  return apiRequest<EducationRecord[]>(
    `/students/profiles/${profileId}/education-history`,
  );
}

export async function createEducation(
  profileId: string,
  payload: Omit<EducationRecord, "id" | "student_profile_id">,
): Promise<EducationRecord> {
  return apiRequest<EducationRecord>(
    `/students/profiles/${profileId}/education-history`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export async function updateEducation(
  profileId: string,
  recordId: string,
  payload: Omit<EducationRecord, "id" | "student_profile_id">,
): Promise<EducationRecord> {
  return apiRequest<EducationRecord>(
    `/students/profiles/${profileId}/education-history/${recordId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export async function deleteEducation(
  profileId: string,
  recordId: string,
): Promise<void> {
  return apiRequest<void>(
    `/students/profiles/${profileId}/education-history/${recordId}`,
    { method: "DELETE" },
  );
}

export async function fetchResumes(profileId: string): Promise<Resume[]> {
  return apiRequest<Resume[]>(`/students/profiles/${profileId}/resumes`);
}

export async function createResume(
  profileId: string,
  payload: Omit<
    Resume,
    "id" | "student_profile_id" | "last_used" | "uploaded_at"
  >,
): Promise<Resume> {
  return apiRequest<Resume>(`/students/profiles/${profileId}/resumes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function uploadResume(
  profileId: string,
  file: File,
  options: { name?: string; is_active?: boolean } = {},
  onProgress: (pct: number) => void = () => undefined,
): Promise<Resume> {
  const { uploadWithProgress, parseUploadError } =
    await import("@/components/ui/file-upload");
  const form = new FormData();
  form.append("file", file);
  if (options.name) form.append("name", options.name);
  if (options.is_active != null) {
    form.append("is_active", String(options.is_active));
  }
  const response = await uploadWithProgress(
    `/api/v1/students/profiles/${profileId}/resumes/upload`,
    form,
    onProgress,
  );
  if (!response.ok) {
    throw new Error(await parseUploadError(response));
  }
  return response.json() as Promise<Resume>;
}

export async function replaceResumeFile(
  profileId: string,
  resumeId: string,
  file: File,
  onProgress: (pct: number) => void = () => undefined,
): Promise<Resume> {
  const { uploadWithProgress, parseUploadError } =
    await import("@/components/ui/file-upload");
  const form = new FormData();
  form.append("file", file);
  const response = await uploadWithProgress(
    `/api/v1/students/profiles/${profileId}/resumes/${resumeId}/replace`,
    form,
    onProgress,
  );
  if (!response.ok) {
    throw new Error(await parseUploadError(response));
  }
  return response.json() as Promise<Resume>;
}

export async function updateResume(
  profileId: string,
  resumeId: string,
  payload: Partial<{
    name: string;
    file_url: string;
    version: number;
    is_active: boolean;
  }>,
): Promise<Resume> {
  return apiRequest<Resume>(
    `/students/profiles/${profileId}/resumes/${resumeId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export async function deleteResume(
  profileId: string,
  resumeId: string,
): Promise<void> {
  return apiRequest<void>(
    `/students/profiles/${profileId}/resumes/${resumeId}`,
    { method: "DELETE" },
  );
}

export async function fetchDocuments(
  profileId: string,
): Promise<StudentDocument[]> {
  return apiRequest<StudentDocument[]>(
    `/students/profiles/${profileId}/documents`,
  );
}

export async function createDocument(
  profileId: string,
  payload: { document_type: string; file_url: string; file_name: string },
): Promise<StudentDocument> {
  return apiRequest<StudentDocument>(
    `/students/profiles/${profileId}/documents`,
    { method: "POST", body: JSON.stringify(payload) },
  );
}

export async function uploadDocument(
  profileId: string,
  file: File,
  options: { document_type: string; file_name?: string },
  onProgress: (pct: number) => void = () => undefined,
): Promise<StudentDocument> {
  const { uploadWithProgress, parseUploadError } =
    await import("@/components/ui/file-upload");
  const form = new FormData();
  form.append("file", file);
  form.append("document_type", options.document_type);
  if (options.file_name) form.append("file_name", options.file_name);
  const response = await uploadWithProgress(
    `/api/v1/students/profiles/${profileId}/documents/upload`,
    form,
    onProgress,
  );
  if (!response.ok) {
    throw new Error(await parseUploadError(response));
  }
  return response.json() as Promise<StudentDocument>;
}

export async function updateDocument(
  profileId: string,
  documentId: string,
  payload: Partial<{
    file_url: string;
    file_name: string;
    status: string;
  }>,
): Promise<StudentDocument> {
  return apiRequest<StudentDocument>(
    `/students/profiles/${profileId}/documents/${documentId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export async function deleteDocument(
  profileId: string,
  documentId: string,
): Promise<void> {
  return apiRequest<void>(
    `/students/profiles/${profileId}/documents/${documentId}`,
    { method: "DELETE" },
  );
}

export async function fetchSkills(profileId: string): Promise<Skill[]> {
  return apiRequest<Skill[]>(`/students/profiles/${profileId}/skills`);
}

export async function createSkill(
  profileId: string,
  payload: { skill_name: string; skill_level: string },
): Promise<Skill> {
  return apiRequest<Skill>(`/students/profiles/${profileId}/skills`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSkill(
  profileId: string,
  skillId: string,
  payload: { skill_name: string; skill_level: string },
): Promise<Skill> {
  return apiRequest<Skill>(
    `/students/profiles/${profileId}/skills/${skillId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export async function deleteSkill(
  profileId: string,
  skillId: string,
): Promise<void> {
  return apiRequest<void>(`/students/profiles/${profileId}/skills/${skillId}`, {
    method: "DELETE",
  });
}

export async function fetchProjects(profileId: string): Promise<Project[]> {
  return apiRequest<Project[]>(`/students/profiles/${profileId}/projects`);
}

export async function createProject(
  profileId: string,
  payload: Omit<Project, "id" | "student_profile_id">,
): Promise<Project> {
  return apiRequest<Project>(`/students/profiles/${profileId}/projects`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProject(
  profileId: string,
  projectId: string,
  payload: Partial<Omit<Project, "id" | "student_profile_id">>,
): Promise<Project> {
  return apiRequest<Project>(
    `/students/profiles/${profileId}/projects/${projectId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export async function deleteProject(
  profileId: string,
  projectId: string,
): Promise<void> {
  return apiRequest<void>(
    `/students/profiles/${profileId}/projects/${projectId}`,
    { method: "DELETE" },
  );
}

export async function fetchVerification(
  profileId: string,
): Promise<Verification> {
  return apiRequest<Verification>(
    `/students/profiles/${profileId}/verification`,
  );
}
