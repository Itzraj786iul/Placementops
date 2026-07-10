"use client";

import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CrmEmptyState } from "@/features/company-crm/components/empty-state";
import { TabContentSkeleton } from "@/features/company-crm/components/loading-skeleton";
import type { CompanyContact } from "@/features/company-crm/types";

type ContactCardProps = {
  contact: CompanyContact;
};

export function ContactCard({ contact }: ContactCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-medium">{contact.name}</h4>
            {contact.is_primary && (
              <Badge variant="secondary" className="text-xs">
                Primary
              </Badge>
            )}
          </div>
          {contact.designation && (
            <p className="text-muted-foreground text-sm">
              {contact.designation}
            </p>
          )}
        </div>
      </div>
      <dl className="mt-3 space-y-1 text-sm">
        {contact.email && (
          <div>
            <dt className="sr-only">Email</dt>
            <dd>{contact.email}</dd>
          </div>
        )}
        {contact.phone && (
          <div>
            <dt className="sr-only">Phone</dt>
            <dd>{contact.phone}</dd>
          </div>
        )}
        {contact.linkedin && (
          <dd>
            <a
              href={contact.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary inline-flex items-center gap-1"
            >
              LinkedIn <ExternalLink className="h-3 w-3" />
            </a>
          </dd>
        )}
      </dl>
    </div>
  );
}

type ContactsTabProps = {
  contacts: CompanyContact[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onAddContact: () => void;
};

export function ContactsTab({
  contacts,
  isLoading,
  isError,
  onRetry,
  onAddContact,
}: ContactsTabProps) {
  if (isLoading) return <TabContentSkeleton />;

  if (isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Failed to load contacts.</p>
        <button type="button" onClick={onRetry} className="mt-2 underline">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex justify-end">
        <Button type="button" size="sm" onClick={onAddContact}>
          Add Contact
        </Button>
      </div>
      {!contacts?.length ? (
        <CrmEmptyState
          title="No contacts added"
          description="Add HR contacts for this company."
          action={
            <Button type="button" size="sm" onClick={onAddContact}>
              Add Contact
            </Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {contacts.map((c) => (
            <ContactCard key={c.id} contact={c} />
          ))}
        </div>
      )}
    </div>
  );
}
