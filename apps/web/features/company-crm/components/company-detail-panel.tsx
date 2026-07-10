"use client";

import * as React from "react";

import { ActionSheets } from "@/features/company-crm/components/action-sheets";
import {
  CompanyDetail,
  useLazyTab,
} from "@/features/company-crm/components/company-detail";
import { CompanyDetailSkeleton } from "@/features/company-crm/components/loading-skeleton";
import { ContactsTab } from "@/features/company-crm/components/tabs/contacts-tab";
import { DocumentsTab } from "@/features/company-crm/components/tabs/documents-tab";
import { HistoryTab } from "@/features/company-crm/components/tabs/history-tab";
import { OverviewTab } from "@/features/company-crm/components/tabs/overview-tab";
import { TimelineTab } from "@/features/company-crm/components/tabs/timeline-tab";
import { useCompanyContacts } from "@/features/company-crm/hooks/use-company-contacts";
import { useCompanyDetail } from "@/features/company-crm/hooks/use-company-detail";
import { useCompanyTimeline } from "@/features/company-crm/hooks/use-company-timeline";
import { useDocumentCache } from "@/features/company-crm/hooks/use-document-cache";
import type { CrmTab } from "@/features/company-crm/types";

type CompanyDetailPanelProps = {
  companyId: string | null;
  activeTab: CrmTab;
  onTabChange: (tab: CrmTab) => void;
};

export function CompanyDetailPanel({
  companyId,
  activeTab,
  onTabChange,
}: CompanyDetailPanelProps) {
  const [activeSheet, setActiveSheet] = React.useState<string | null>(null);
  const { addDocument, getDocuments } = useDocumentCache();

  const detail = useCompanyDetail(companyId);
  const contactsEnabled = useLazyTab(activeTab, "contacts");
  const timelineEnabled = useLazyTab(activeTab, "timeline");

  const contacts = useCompanyContacts(companyId, contactsEnabled);
  const timeline = useCompanyTimeline(companyId, timelineEnabled);

  const openSheet = (sheet: string) => setActiveSheet(sheet);
  const closeSheet = () => setActiveSheet(null);

  if (!companyId) {
    return (
      <CompanyDetail
        companyName={null}
        activeTab={activeTab}
        onTabChange={onTabChange}
      >
        {null}
      </CompanyDetail>
    );
  }

  if (detail.isLoading) {
    return <CompanyDetailSkeleton />;
  }

  if (detail.isError || !detail.data) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Failed to load company details.</p>
        <button
          type="button"
          onClick={() => detail.refetch()}
          className="mt-2 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  const company = detail.data;

  return (
    <>
      <CompanyDetail
        companyName={company.name}
        activeTab={activeTab}
        onTabChange={onTabChange}
      >
        {activeTab === "overview" && (
          <OverviewTab
            company={company}
            onEdit={() => openSheet("edit")}
            onUpdatePipeline={() => openSheet("pipeline")}
            onAssignHandler={() => openSheet("handler")}
          />
        )}
        {activeTab === "contacts" && contactsEnabled && (
          <ContactsTab
            contacts={contacts.data}
            isLoading={contacts.isLoading}
            isError={contacts.isError}
            onRetry={() => contacts.refetch()}
            onAddContact={() => openSheet("contact")}
          />
        )}
        {activeTab === "timeline" && timelineEnabled && (
          <TimelineTab
            timeline={timeline.data}
            isLoading={timeline.isLoading}
            isError={timeline.isError}
            onRetry={() => timeline.refetch()}
            onAddCommunication={() => openSheet("communication")}
          />
        )}
        {activeTab === "documents" && (
          <DocumentsTab
            documents={getDocuments(companyId)}
            onUpload={() => openSheet("document")}
          />
        )}
        {activeTab === "history" && <HistoryTab company={company} />}
      </CompanyDetail>

      <ActionSheets
        company={company}
        companyId={companyId}
        activeSheet={activeSheet}
        onClose={closeSheet}
        onDocumentUploaded={addDocument}
      />
    </>
  );
}
