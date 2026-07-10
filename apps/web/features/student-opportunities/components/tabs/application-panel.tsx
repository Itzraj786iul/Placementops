"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/features/student-opportunities/components/confirm-dialog";
import { QuestionRenderer } from "@/features/student-opportunities/components/question-renderer";
import { ResumeSelector } from "@/features/student-opportunities/components/resume-selector";
import { StatusBadge } from "@/features/student-opportunities/components/status-badge";
import {
  BACKEND_LIMITATIONS,
  TERMINAL_APPLICATION_STATUSES,
} from "@/features/student-opportunities/constants";
import { useApplicationMutations } from "@/features/student-opportunities/hooks/use-applications";
import type {
  ApplicationListItem,
  EligibilityCheck,
} from "@/features/student-opportunities/types";
import type { Resume } from "@/features/student-onboarding/types";
import { isDeadlinePassed } from "@/features/student-opportunities/utils/filter-opportunities";

type ApplicationPanelProps = {
  opportunityId: string;
  application: ApplicationListItem | undefined;
  resumes: Resume[];
  resumesLoading: boolean;
  eligibility: EligibilityCheck;
  deadline: string;
};

function canWithdraw(status: ApplicationListItem["status"]): boolean {
  return !TERMINAL_APPLICATION_STATUSES.includes(status);
}

export function ApplicationPanel({
  opportunityId,
  application,
  resumes,
  resumesLoading,
  eligibility,
  deadline,
}: ApplicationPanelProps) {
  const [resumeId, setResumeId] = React.useState("");
  const [confirmOpen, setConfirmOpen] = React.useState(false);
  const [withdrawOpen, setWithdrawOpen] = React.useState(false);
  const { apply, withdraw } = useApplicationMutations();

  const selectedResume = resumes.find((r) => r.id === resumeId);

  const handleApply = async () => {
    if (!resumeId) {
      toast.error("Select a resume before applying.");
      return;
    }
    try {
      await apply.mutateAsync({
        opportunityId,
        payload: { selected_resume_id: resumeId, answers: [] },
      });
      toast.success("Application submitted successfully.");
      setConfirmOpen(false);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to submit application.",
      );
    }
  };

  const handleWithdraw = async () => {
    if (!application) return;
    try {
      await withdraw.mutateAsync({
        applicationId: application.id,
        opportunityId,
      });
      toast.success("Application withdrawn.");
      setWithdrawOpen(false);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to withdraw application.",
      );
    }
  };

  if (application) {
    const resumeUsed = resumes.find(
      (r) => r.id === application.selected_resume_id,
    );

    return (
      <div className="space-y-4 p-4">
        <div className="rounded-lg border p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium">Status</span>
            <StatusBadge status={application.status} />
          </div>
          <dl className="mt-4 space-y-2 text-sm">
            <div>
              <dt className="text-muted-foreground">Applied at</dt>
              <dd>{new Date(application.applied_at).toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Resume used</dt>
              <dd>{resumeUsed?.name ?? application.selected_resume_id}</dd>
            </div>
          </dl>
        </div>
        {canWithdraw(application.status) && (
          <>
            <Button
              type="button"
              variant="outline"
              className="text-destructive"
              onClick={() => setWithdrawOpen(true)}
            >
              Withdraw application
            </Button>
            <ConfirmDialog
              open={withdrawOpen}
              title="Withdraw application?"
              description="This action cannot be undone. You may not be able to re-apply depending on drive rules."
              confirmLabel="Withdraw"
              loading={withdraw.isPending}
              onConfirm={handleWithdraw}
              onCancel={() => setWithdrawOpen(false)}
            />
          </>
        )}
      </div>
    );
  }

  const deadlinePassed = isDeadlinePassed(deadline);

  return (
    <div className="space-y-4 p-4">
      {!eligibility.eligible && (
        <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-800 dark:text-amber-200">
          Review eligibility before applying. You may still submit, but your
          application could be rejected if criteria are not met.
        </p>
      )}

      <p className="text-muted-foreground text-sm">
        {BACKEND_LIMITATIONS.noQuestionsList}
      </p>

      {resumesLoading ? (
        <p className="text-muted-foreground text-sm">Loading resumes...</p>
      ) : (
        <ResumeSelector
          resumes={resumes}
          value={resumeId}
          onChange={setResumeId}
          disabled={apply.isPending}
        />
      )}

      <QuestionRenderer
        questions={[]}
        answers={{}}
        onChange={() => undefined}
      />

      {deadlinePassed ? (
        <p className="text-destructive text-sm">
          The application deadline has passed.
        </p>
      ) : (
        <Button
          type="button"
          disabled={!resumeId || apply.isPending}
          onClick={() => setConfirmOpen(true)}
        >
          Apply
        </Button>
      )}

      <ConfirmDialog
        open={confirmOpen}
        title="Confirm application"
        description={`Submit your application${selectedResume ? ` with resume "${selectedResume.name}"` : ""}?`}
        confirmLabel="Submit application"
        loading={apply.isPending}
        onConfirm={handleApply}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}
