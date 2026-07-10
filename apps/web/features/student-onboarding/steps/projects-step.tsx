"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import * as React from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { EmptyState } from "@/features/student-onboarding/components/empty-state";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { ProjectCard } from "@/features/student-onboarding/components/project-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  createProject,
  deleteProject,
  updateProject,
} from "@/features/student-onboarding/api/student-client";
import {
  projectSchema,
  type ProjectValues,
} from "@/features/student-onboarding/schemas/onboarding-schemas";
import type { Project } from "@/features/student-onboarding/types";
import { nullifyEmpty } from "@/features/student-onboarding/utils/payload-helpers";

export function ProjectsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { projects } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [editing, setEditing] = React.useState<Project | null>(null);
  const [showForm, setShowForm] = React.useState(false);

  const refresh = async () => {
    await invalidateAll(profileId);
    setEditing(null);
    setShowForm(false);
  };

  if (projects.isLoading) return <StepSkeleton />;

  return (
    <SectionCard title="Projects" description="Showcase your best work.">
      {!projects.data?.length && !showForm ? (
        <EmptyState
          title="No projects yet"
          description="Add projects with tech stack and links."
          action={
            !isReadOnly && (
              <Button type="button" onClick={() => setShowForm(true)}>
                Add Project
              </Button>
            )
          }
        />
      ) : (
        <div className="space-y-4">
          {projects.data?.map((project) =>
            editing?.id === project.id ? null : (
              <ProjectCard
                key={project.id}
                project={project}
                isReadOnly={isReadOnly}
                onEdit={() => setEditing(project)}
                onDelete={async () => {
                  await deleteProject(profileId, project.id);
                  await refresh();
                }}
              />
            ),
          )}
        </div>
      )}
      {!isReadOnly && (showForm || editing) && (
        <ProjectForm
          project={editing}
          onCancel={() => {
            setEditing(null);
            setShowForm(false);
          }}
          onSaved={refresh}
        />
      )}
      {!isReadOnly && projects.data?.length && !showForm && !editing && (
        <Button
          type="button"
          variant="outline"
          className="mt-4"
          onClick={() => setShowForm(true)}
        >
          Add Project
        </Button>
      )}
    </SectionCard>
  );
}

function ProjectForm({
  project,
  onCancel,
  onSaved,
}: {
  project: Project | null;
  onCancel: () => void;
  onSaved: () => Promise<void>;
}) {
  const { profileId } = useOnboarding();
  const form = useForm<ProjectValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: "",
      description: "",
      tech_stack: "",
      github_url: "",
      demo_url: "",
    },
  });

  React.useEffect(() => {
    if (project) {
      form.reset({
        title: project.title,
        description: project.description,
        tech_stack: project.tech_stack,
        github_url: project.github_url ?? "",
        demo_url: project.demo_url ?? "",
      });
    }
  }, [project, form]);

  const onSubmit = form.handleSubmit(async (data) => {
    const payload = {
      ...data,
      github_url: nullifyEmpty(data.github_url),
      demo_url: nullifyEmpty(data.demo_url),
    };
    if (project) {
      await updateProject(profileId, project.id, payload);
    } else {
      await createProject(profileId, payload);
    }
    await onSaved();
  });

  return (
    <form
      onSubmit={onSubmit}
      className="mt-6 grid gap-3 rounded-lg border p-4 sm:grid-cols-2"
    >
      <FormField
        label="Title"
        error={form.formState.errors.title?.message}
        className="sm:col-span-2"
      >
        <Input {...form.register("title")} />
      </FormField>
      <FormField
        label="Description"
        error={form.formState.errors.description?.message}
        className="sm:col-span-2"
      >
        <Textarea {...form.register("description")} />
      </FormField>
      <FormField
        label="Technology Stack"
        error={form.formState.errors.tech_stack?.message}
        className="sm:col-span-2"
      >
        <Input
          {...form.register("tech_stack")}
          placeholder="React, Python, PostgreSQL"
        />
      </FormField>
      <FormField
        label="GitHub URL"
        error={form.formState.errors.github_url?.message}
      >
        <Input
          {...form.register("github_url")}
          placeholder="https://github.com/..."
        />
      </FormField>
      <FormField
        label="Live Demo URL"
        error={form.formState.errors.demo_url?.message}
      >
        <Input {...form.register("demo_url")} placeholder="https://..." />
      </FormField>
      <div className="flex gap-2 sm:col-span-2">
        <Button type="submit" size="sm">
          Save Project
        </Button>
        <Button type="button" size="sm" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
