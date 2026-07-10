"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { EmptyState } from "@/features/student-onboarding/components/empty-state";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  SKILL_LEVELS,
  SKILL_SUGGESTIONS,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  createSkill,
  deleteSkill,
} from "@/features/student-onboarding/api/student-client";

export function SkillsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { skills } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [input, setInput] = React.useState("");
  const [level, setLevel] = React.useState(SKILL_LEVELS[1]);
  const [showSuggestions, setShowSuggestions] = React.useState(false);

  const refresh = async () => {
    await invalidateAll(profileId);
  };

  const addSkill = async (name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    const exists = skills.data?.some(
      (s) => s.skill_name.toLowerCase() === trimmed.toLowerCase(),
    );
    if (exists) return;
    await createSkill(profileId, { skill_name: trimmed, skill_level: level });
    setInput("");
    setShowSuggestions(false);
    await refresh();
  };

  const removeSkill = async (skillId: string) => {
    await deleteSkill(profileId, skillId);
    await refresh();
  };

  const filteredSuggestions = SKILL_SUGGESTIONS.filter(
    (s) =>
      s.toLowerCase().includes(input.toLowerCase()) &&
      !skills.data?.some(
        (sk) => sk.skill_name.toLowerCase() === s.toLowerCase(),
      ),
  );

  if (skills.isLoading) return <StepSkeleton />;

  return (
    <SectionCard
      title="Skills"
      description="Add skills relevant to your placement profile."
    >
      {!isReadOnly && (
        <div className="relative mb-6 space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row">
            <Input
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                setShowSuggestions(true);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  void addSkill(input);
                }
              }}
              placeholder="Type a skill and press Enter"
              aria-label="Add skill"
            />
            <Select value={level} onChange={(e) => setLevel(e.target.value)}>
              {SKILL_LEVELS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </Select>
            <Button type="button" onClick={() => addSkill(input)}>
              Add
            </Button>
          </div>
          {showSuggestions && input && filteredSuggestions.length > 0 && (
            <ul className="bg-background absolute z-10 mt-1 w-full rounded-md border shadow-sm sm:max-w-md">
              {filteredSuggestions.slice(0, 6).map((suggestion) => (
                <li key={suggestion}>
                  <button
                    type="button"
                    className="hover:bg-muted w-full px-3 py-2 text-left text-sm"
                    onClick={() => addSkill(suggestion)}
                  >
                    {suggestion}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {!skills.data?.length ? (
        <EmptyState
          title="No skills added"
          description="Start typing to add skills with proficiency levels."
        />
      ) : (
        <div className="flex flex-wrap gap-2">
          {skills.data.map((skill) => (
            <span
              key={skill.id}
              className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm"
            >
              {skill.skill_name}
              <span className="text-muted-foreground text-xs">
                {skill.skill_level}
              </span>
              {!isReadOnly && (
                <button
                  type="button"
                  onClick={() => removeSkill(skill.id)}
                  className="text-muted-foreground hover:text-destructive"
                  aria-label={`Remove ${skill.skill_name}`}
                >
                  ×
                </button>
              )}
            </span>
          ))}
        </div>
      )}
    </SectionCard>
  );
}
