"use client";

import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { SlideOver } from "@/features/company-crm/components/slide-over";
import { EligibilityReasonsTable } from "@/features/eligibility/components/eligibility-reasons-table";
import { EligibilityResultBanner } from "@/features/eligibility/components/eligibility-result-banner";
import { EligibilitySnapshotPanel } from "@/features/eligibility/components/eligibility-snapshot-panel";
import { useStudentEligibilityEvaluation } from "@/features/eligibility/hooks/use-eligibility-engine";
import { fetchApplicationDetail } from "@/features/convener-opportunities/api/operations-client";
import { BACKEND_LIMITATIONS } from "@/features/convener-opportunities/constants";
import type { ApplicationSnapshot } from "@/features/convener-opportunities/types";
import { getStudentName } from "@/features/convener-opportunities/utils/application-utils";
import { StatusBadge } from "@/features/student-opportunities/components/status-badge";

type StudentDrawerProps = {
  applicationId: string | null;
  opportunityId: string;
  studentProfileId?: string;
  snapshot?: ApplicationSnapshot;
  onClose: () => void;
};

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-muted-foreground text-xs font-medium">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}

export function StudentDrawer({
  applicationId,
  opportunityId,
  studentProfileId,
  snapshot,
  onClose,
}: StudentDrawerProps) {
  const detailQuery = useQuery({
    queryKey: [
      "convener-opportunities",
      "application-detail",
      applicationId ?? "",
    ],
    queryFn: () => fetchApplicationDetail(applicationId!),
    enabled: Boolean(applicationId),
    staleTime: 60_000,
  });

  const profileId =
    studentProfileId ??
    snapshot?.student_profile_snapshot.id ??
    detailQuery.data?.student_profile_id;

  const evaluationQuery = useStudentEligibilityEvaluation(
    opportunityId,
    profileId,
    Boolean(applicationId) && Boolean(profileId),
  );

  const profile = snapshot?.student_profile_snapshot;
  const personal = profile?.personal_information;
  const academic = profile?.academic_information;
  const resume = snapshot?.resume_snapshot;

  return (
    <SlideOver
      open={Boolean(applicationId)}
      onClose={onClose}
      title={getStudentName(snapshot)}
      description={
        profile?.roll_number ? `Roll ${profile.roll_number}` : undefined
      }
    >
      {detailQuery.isLoading && !snapshot ? (
        <p className="text-muted-foreground text-sm">Loading application...</p>
      ) : (
        <div className="space-y-6">
          <section>
            <h3 className="mb-3 text-sm font-semibold">Profile summary</h3>
            <dl className="grid gap-3 sm:grid-cols-2">
              <Field label="Name" value={getStudentName(snapshot)} />
              <Field label="Roll number" value={profile?.roll_number ?? "—"} />
              <Field
                label="Department"
                value={profile?.department_name ?? "—"}
              />
              <Field
                label="Branch code"
                value={profile?.department_code ?? "—"}
              />
              <Field label="CGPA" value={academic?.current_cgpa ?? "—"} />
              <Field
                label="Graduation year"
                value={profile?.graduation_year ?? "—"}
              />
              <Field label="Email" value={personal?.personal_email ?? "—"} />
              <Field label="Gender" value={personal?.gender ?? "—"} />
            </dl>
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold">Resume used</h3>
            {resume ? (
              <div className="rounded-lg border p-3 text-sm">
                <p className="font-medium">
                  {resume.name} (v{resume.version})
                </p>
                <a
                  href={resume.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary mt-2 inline-block underline-offset-4 hover:underline"
                >
                  Open resume
                </a>
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">
                Resume snapshot unavailable.
              </p>
            )}
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold">Application snapshot</h3>
            {detailQuery.data ? (
              <dl className="grid gap-3 sm:grid-cols-2">
                <Field
                  label="Applied at"
                  value={new Date(detailQuery.data.applied_at).toLocaleString()}
                />
                <div>
                  <dt className="text-muted-foreground text-xs font-medium">
                    Status
                  </dt>
                  <dd className="mt-1">
                    <StatusBadge status={detailQuery.data.status} />
                  </dd>
                </div>
              </dl>
            ) : detailQuery.isError ? (
              <div className="text-sm">
                <p className="text-destructive">
                  Could not load application detail.
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => detailQuery.refetch()}
                >
                  Retry
                </Button>
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">Loading...</p>
            )}
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold">Eligibility snapshot</h3>
            <EligibilitySnapshotPanel
              snapshot={snapshot?.eligibility_snapshot}
            />
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold">Eligibility result</h3>
            {evaluationQuery.isLoading ? (
              <p className="text-muted-foreground text-sm">
                Evaluating eligibility...
              </p>
            ) : evaluationQuery.isError ? (
              <div className="text-sm">
                <p className="text-destructive">
                  Could not evaluate eligibility.
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => evaluationQuery.refetch()}
                >
                  Retry
                </Button>
              </div>
            ) : evaluationQuery.data ? (
              <div className="space-y-3">
                <EligibilityResultBanner
                  eligible={evaluationQuery.data.eligible}
                />
                {!evaluationQuery.data.eligible && (
                  <EligibilityReasonsTable
                    reasons={evaluationQuery.data.reasons}
                  />
                )}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">
                Eligibility result unavailable for this student.
              </p>
            )}
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold">Custom answers</h3>
            {detailQuery.data?.answers.length ? (
              <ul className="space-y-2">
                {detailQuery.data.answers.map((answer) => (
                  <li key={answer.id} className="rounded-lg border p-3 text-sm">
                    <p className="text-muted-foreground text-xs">
                      Question {answer.application_question_id.slice(0, 8)}…
                    </p>
                    <p className="mt-1">{answer.answer}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground text-sm">
                {BACKEND_LIMITATIONS.noApplicationQuestions}
              </p>
            )}
          </section>
        </div>
      )}
    </SlideOver>
  );
}
