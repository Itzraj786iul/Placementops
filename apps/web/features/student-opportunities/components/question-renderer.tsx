"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import type { QuestionType } from "@/features/student-opportunities/types";

export type QuestionField = {
  id: string;
  question: string;
  question_type: QuestionType;
  is_required: boolean;
  choices?: string[] | null;
};

type QuestionRendererProps = {
  questions: QuestionField[];
  answers: Record<string, string>;
  onChange: (questionId: string, value: string) => void;
  disabled?: boolean;
};

export function QuestionRenderer({
  questions,
  answers,
  onChange,
  disabled = false,
}: QuestionRendererProps) {
  if (questions.length === 0) return null;

  return (
    <div className="space-y-4">
      {questions.map((q) => (
        <div key={q.id} className="space-y-2">
          <Label htmlFor={`q-${q.id}`}>
            {q.question}
            {q.is_required && <span className="text-destructive"> *</span>}
          </Label>
          {q.question_type === "BOOLEAN" ? (
            <Select
              id={`q-${q.id}`}
              value={answers[q.id] ?? ""}
              disabled={disabled}
              onChange={(e) => onChange(q.id, e.target.value)}
            >
              <option value="">Select</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </Select>
          ) : q.question_type === "CHOICE" && q.choices?.length ? (
            <Select
              id={`q-${q.id}`}
              value={answers[q.id] ?? ""}
              disabled={disabled}
              onChange={(e) => onChange(q.id, e.target.value)}
            >
              <option value="">Select</option>
              {q.choices.map((choice) => (
                <option key={choice} value={choice}>
                  {choice}
                </option>
              ))}
            </Select>
          ) : (
            <Input
              id={`q-${q.id}`}
              type={q.question_type === "NUMBER" ? "number" : "text"}
              value={answers[q.id] ?? ""}
              disabled={disabled}
              onChange={(e) => onChange(q.id, e.target.value)}
            />
          )}
        </div>
      ))}
    </div>
  );
}
