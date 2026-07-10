"use client";

import * as React from "react";
import { useMemo } from "react";

import { Button } from "@/components/ui/button";
import { ExportDialog } from "@/features/convener-opportunities/components/export-dialog";
import { ImportDialog } from "@/features/convener-opportunities/components/import-dialog";
import { OpportunityHeader } from "@/features/convener-opportunities/components/opportunity-header";
import {
  OperationsTabShell,
  useLazyOperationsTab,
} from "@/features/convener-opportunities/components/operations-tab-shell";
import { StudentDrawer } from "@/features/convener-opportunities/components/student-drawer";
import { SummaryCard } from "@/features/convener-opportunities/components/summary-card";
import { ApplicationsPanel } from "@/features/convener-opportunities/components/tabs/applications-panel";
import { DocumentsPanel } from "@/features/convener-opportunities/components/tabs/documents-panel";
import { OverviewPanel } from "@/features/convener-opportunities/components/tabs/overview-panel";
import { ScreeningPanel } from "@/features/convener-opportunities/components/tabs/screening-panel";
import { TimelinePanel } from "@/features/convener-opportunities/components/tabs/timeline-panel";
import {
  OperationsHeaderSkeleton,
  SummaryCardsSkeleton,
} from "@/features/convener-opportunities/components/loading-skeleton";
import {
  OPPORTUNITY_STATUS_LABELS,
  TIMELINE_STAGE_LABELS,
} from "@/features/convener-opportunities/constants";
import {
  useApplicationSnapshots,
  useOpportunityApplications,
  useOpportunityEligibility,
  useOpportunityOperations,
  useOpportunityTimeline,
} from "@/features/convener-opportunities/hooks/use-opportunity-operations";
import type { OperationsTab } from "@/features/convener-opportunities/types";
import {
  enrichApplications,
  extractDepartments,
} from "@/features/convener-opportunities/utils/application-utils";
import { isDeadlinePassed } from "@/features/student-opportunities/utils/filter-opportunities";

type OpportunityOperationsWorkspaceProps = {
  opportunityId: string;
};

export function OpportunityOperationsWorkspace({
  opportunityId,
}: OpportunityOperationsWorkspaceProps) {
  const [activeTab, setActiveTab] = React.useState<OperationsTab>("overview");
  const [selectedApplicationId, setSelectedApplicationId] = React.useState<
    string | null
  >(null);
  const [exportOpen, setExportOpen] = React.useState(false);
  const [importOpen, setImportOpen] = React.useState(false);

  const applicationsTabEnabled = useLazyOperationsTab(
    activeTab,
    "applications",
  );
  const timelineTabEnabled = useLazyOperationsTab(activeTab, "timeline");
  const screeningTabEnabled = useLazyOperationsTab(activeTab, "screening");

  const { opportunity, companyName } = useOpportunityOperations(opportunityId);
  const applicationsQuery = useOpportunityApplications(
    opportunityId,
    applicationsTabEnabled || activeTab === "overview",
  );
  const eligibilityQuery = useOpportunityEligibility(opportunityId);
  const timelineQuery = useOpportunityTimeline(
    opportunityId,
    timelineTabEnabled || activeTab === "overview",
  );

  const applicationIds = useMemo(
    () => (applicationsQuery.data ?? []).map((app) => app.id),
    [applicationsQuery.data],
  );

  const snapshotQueries = useApplicationSnapshots(
    applicationIds,
    applicationsTabEnabled && applicationIds.length > 0,
  );

  const snapshotsMap = useMemo(() => {
    const map = new Map<
      string,
      NonNullable<(typeof snapshotQueries)[number]["data"]>
    >();
    applicationIds.forEach((id, index) => {
      const data = snapshotQueries[index]?.data;
      if (data) map.set(id, data);
    });
    return map;
  }, [applicationIds, snapshotQueries]);

  const enrichedApplications = useMemo(
    () => enrichApplications(applicationsQuery.data ?? [], snapshotsMap),
    [applicationsQuery.data, snapshotsMap],
  );

  const exportDepartments = useMemo(
    () => extractDepartments(enrichedApplications),
    [enrichedApplications],
  );

  const selectedSnapshot = selectedApplicationId
    ? snapshotsMap.get(selectedApplicationId)
    : undefined;

  const selectedApplication = selectedApplicationId
    ? enrichedApplications.find(
        (item) => item.application.id === selectedApplicationId,
      )?.application
    : undefined;

  const handleRefresh = () => {
    void opportunity.refetch();
    void companyName.refetch();
    void applicationsQuery.refetch();
    void eligibilityQuery.refetch();
    void timelineQuery.refetch();
  };

  const isRefreshing =
    opportunity.isFetching ||
    companyName.isFetching ||
    applicationsQuery.isFetching;

  if (opportunity.isLoading || companyName.isLoading) {
    return (
      <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
        <OperationsHeaderSkeleton />
        <SummaryCardsSkeleton />
      </div>
    );
  }

  if (opportunity.isError || !opportunity.data) {
    return (
      <div className="-m-6 flex min-h-[50vh] flex-col items-center justify-center p-6 text-center">
        <p className="text-destructive">Could not load this opportunity.</p>
        <Button
          type="button"
          variant="outline"
          className="mt-4"
          onClick={() => opportunity.refetch()}
        >
          Retry
        </Button>
      </div>
    );
  }

  const opportunityWithCompany = {
    ...opportunity.data,
    companyName: companyName.data ?? "Unknown company",
  };

  const applicationCount = applicationsQuery.data?.length ?? 0;
  const deadlinePassed = isDeadlinePassed(
    opportunity.data.application_deadline,
  );
  const currentStage = opportunity.data.current_timeline_stage;

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <OpportunityHeader
        opportunity={opportunityWithCompany}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
        onExport={() => setExportOpen(true)}
        onImport={() => setImportOpen(true)}
      />

      <div className="grid gap-4 border-b px-6 py-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard label="Applications received" value={applicationCount} />
        <SummaryCard
          label="Published status"
          value={OPPORTUNITY_STATUS_LABELS[opportunity.data.status]}
        />
        <SummaryCard
          label="Deadline"
          value={new Date(
            opportunity.data.application_deadline,
          ).toLocaleDateString()}
          hint={deadlinePassed ? "Deadline passed" : "Applications open"}
        />
        <SummaryCard
          label="Hiring stage"
          value={currentStage ? TIMELINE_STAGE_LABELS[currentStage] : "Not set"}
        />
      </div>

      <OperationsTabShell
        activeTab={activeTab}
        onTabChange={setActiveTab}
        applicationCount={applicationCount}
      >
        {activeTab === "overview" && (
          <OverviewPanel
            opportunity={opportunityWithCompany}
            eligibility={eligibilityQuery.data}
            timeline={timelineQuery.data}
            isLoadingEligibility={eligibilityQuery.isLoading}
            isLoadingTimeline={timelineQuery.isLoading}
          />
        )}
        {activeTab === "applications" && applicationsTabEnabled && (
          <ApplicationsPanel
            enrichedItems={enrichedApplications}
            isLoading={
              applicationsQuery.isLoading ||
              snapshotQueries.some((q) => q.isLoading)
            }
            isError={applicationsQuery.isError}
            onRetry={() => applicationsQuery.refetch()}
            onSelectApplication={setSelectedApplicationId}
          />
        )}
        {activeTab === "screening" && screeningTabEnabled && (
          <ScreeningPanel opportunityId={opportunityId} />
        )}
        {activeTab === "documents" && (
          <DocumentsPanel opportunityId={opportunityId} />
        )}
        {activeTab === "timeline" && timelineTabEnabled && (
          <TimelinePanel
            timeline={timelineQuery.data}
            currentStage={currentStage}
            isLoading={timelineQuery.isLoading}
            isError={timelineQuery.isError}
            onRetry={() => timelineQuery.refetch()}
          />
        )}
      </OperationsTabShell>

      <StudentDrawer
        applicationId={selectedApplicationId}
        opportunityId={opportunityId}
        studentProfileId={
          selectedSnapshot?.student_profile_snapshot.id ??
          selectedApplication?.student_profile_id
        }
        snapshot={selectedSnapshot}
        onClose={() => setSelectedApplicationId(null)}
      />

      <ExportDialog
        open={exportOpen}
        opportunityId={opportunityId}
        companyId={opportunity.data.company_id}
        companyName={opportunityWithCompany.companyName}
        departments={exportDepartments}
        onClose={() => setExportOpen(false)}
      />

      <ImportDialog
        open={importOpen}
        opportunityId={opportunityId}
        onClose={() => setImportOpen(false)}
        onApplied={handleRefresh}
      />
    </div>
  );
}
