"use client";

import { ExternalLink, Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Project } from "@/features/student-onboarding/types";

type ProjectCardProps = {
  project: Project;
  isReadOnly: boolean;
  onEdit: () => void;
  onDelete: () => void;
};

export function ProjectCard({
  project,
  isReadOnly,
  onEdit,
  onDelete,
}: ProjectCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2">
          <h4 className="font-medium">{project.title}</h4>
          <p className="text-muted-foreground line-clamp-2 text-sm">
            {project.description}
          </p>
          <p className="text-muted-foreground text-xs">{project.tech_stack}</p>
          <div className="flex gap-3">
            {project.github_url && (
              <a
                href={project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary inline-flex items-center gap-1 text-xs"
              >
                <ExternalLink className="h-3 w-3" />
                GitHub
              </a>
            )}
            {project.demo_url && (
              <a
                href={project.demo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary inline-flex items-center gap-1 text-xs"
              >
                <ExternalLink className="h-3 w-3" />
                Live Demo
              </a>
            )}
          </div>
        </div>
      </div>
      {!isReadOnly && (
        <div className="mt-4 flex gap-2">
          <Button type="button" size="sm" variant="outline" onClick={onEdit}>
            <Pencil className="h-3.5 w-3.5" />
            Edit
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
