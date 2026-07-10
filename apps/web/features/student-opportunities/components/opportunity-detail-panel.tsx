"use client";

import * as React from "react";

import {
  OpportunityDetailShell,
  useLazyOpportunityTab,
} from "@/features/student-opportunities/components/opportunity-detail";
import { OpportunityDetailSkeleton } from "@/features/student-opportunities/components/loading-skeleton";
import { ApplicationPanel } from "@/features/student-opportunities/components/tabs/application-panel";
import { DocumentsTab } from "@/features/student-opportunities/components/tabs/documents-tab";
import { EligibilityPanel } from "@/features/student-opportunities/components/tabs/eligibility-panel";
import { OverviewTab } from "@/features/student-opportunities/components/tabs/overview-tab";
import {
  useOpportunityDetail,
  useOpportunityEligibility,
} from "@/features/student-opportunities/hooks/use-opportunities";
import { useStudentEligibilityEvaluation } from "@/features/eligibility/hooks/use-eligibility-engine";
import type {
  ApplicationListItem,
  OpportunityTab,
} from "@/features/student-opportunities/types";
import {
  useDepartments,
  useStudentOnboardingData,
  useStudentProfile,
} from "@/features/student-onboarding/hooks/use-student-data";

type OpportunityDetailPanelProps = {
  opportunityId: string | null;
  activeTab: OpportunityTab;
  onTabChange: (tab: OpportunityTab) => void;
  application?: ApplicationListItem;
};

export function OpportunityDetailPanel({
  opportunityId,
  activeTab,
  onTabChange,
  application,
}: OpportunityDetailPanelProps) {
  const eligibilityEnabled = useLazyOpportunityTab(activeTab, "eligibility");
  const applicationEnabled = useLazyOpportunityTab(activeTab, "application");

  const detailQuery = useOpportunityDetail(opportunityId);
  const eligibilityQuery = useOpportunityEligibility(
    opportunityId,
    Boolean(opportunityId) && eligibilityEnabled,
  );

  const profileQuery = useStudentProfile();
  const profileId = profileQuery.data?.id;
  const { resumes } = useStudentOnboardingData(profileId);
  const departmentsQuery = useDepartments();

  const evaluationQuery = useStudentEligibilityEvaluation(
    opportunityId,
    profileId,
    Boolean(opportunityId) &&
      Boolean(profileId) &&
      (eligibilityEnabled || applicationEnabled),
  );

  if (!opportunityId) {
    return (
      <OpportunityDetailShell
        title={null}
        activeTab={activeTab}
        onTabChange={onTabChange}
      >
        {null}
      </OpportunityDetailShell>
    );
  }

  if (detailQuery.isLoading) {
    return <OpportunityDetailSkeleton />;
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Failed to load opportunity details.</p>
        <button
          type="button"
          onClick={() => detailQuery.refetch()}
          className="mt-2 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  const detail = detailQuery.data;
  const evaluation = evaluationQuery.data;
  const eligibilityForApply = {
    eligible: evaluation?.eligible ?? true,
    reasons: evaluation?.reasons.map((r) => r.title) ?? [],
  };

  return (
    <OpportunityDetailShell
      title={detail.title}
      activeTab={activeTab}
      onTabChange={onTabChange}
    >
      {activeTab === "overview" && <OverviewTab detail={detail} />}
      {activeTab === "eligibility" && eligibilityEnabled && (
        <EligibilityPanel
          rule={eligibilityQuery.data}
          evaluation={evaluation}
          departments={departmentsQuery.data ?? []}
          isLoadingRules={eligibilityQuery.isLoading}
          isLoadingEvaluation={evaluationQuery.isLoading}
          isError={eligibilityQuery.isError || evaluationQuery.isError}
          profileMissing={!profileId && !profileQuery.isLoading}
          onRetry={() => {
            void eligibilityQuery.refetch();
            void evaluationQuery.refetch();
          }}
        />
      )}
      {activeTab === "documents" && (
        <DocumentsTab opportunityId={opportunityId} />
      )}
      {activeTab === "application" && applicationEnabled && (
        <ApplicationPanel
          opportunityId={opportunityId}
          application={application}
          resumes={resumes.data ?? []}
          resumesLoading={resumes.isLoading}
          eligibility={eligibilityForApply}
          deadline={detail.application_deadline}
        />
      )}
    </OpportunityDetailShell>
  );
}
