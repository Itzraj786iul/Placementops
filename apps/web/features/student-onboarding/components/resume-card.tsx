"use client";

import { ExternalLink, Star, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Resume } from "@/features/student-onboarding/types";
import { cn } from "@/lib/utils";

type ResumeCardProps = {
  resume: Resume;
  isReadOnly: boolean;
  onActivate: () => void;
  onRename: () => void;
  onDelete: () => void;
};

export function ResumeCard({
  resume,
  isReadOnly,
  onActivate,
  onRename,
  onDelete,
}: ResumeCardProps) {
  const uploadedDate = new Date(resume.uploaded_at).toLocaleDateString();

  return (
    <div
      className={cn(
        "rounded-lg border p-4",
        resume.is_active && "border-primary bg-primary/5",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="font-medium">{resume.name}</h4>
            {resume.is_active && (
              <span className="bg-primary/10 text-primary rounded-full px-2 py-0.5 text-xs font-medium">
                Active
              </span>
            )}
          </div>
          <p className="text-muted-foreground text-xs">
            Version {resume.version} · Uploaded {uploadedDate}
          </p>
        </div>
        <a
          href={resume.file_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-foreground"
          aria-label={`Open ${resume.name}`}
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
      {!isReadOnly && (
        <div className="mt-4 flex flex-wrap gap-2">
          {!resume.is_active && (
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onActivate}
            >
              <Star className="h-3.5 w-3.5" />
              Activate
            </Button>
          )}
          <Button type="button" size="sm" variant="outline" onClick={onRename}>
            Rename
          </Button>
          <Button
            type="button"
            size="sm"
            variant="ghost"
            className="text-destructive"
            onClick={onDelete}
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete
          </Button>
        </div>
      )}
    </div>
  );
}
