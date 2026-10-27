"use client";

import type { ReactNode } from "react";
import type { Question } from "@/lib/api";
import { CodeBlock } from "@/components/CodeBlock";
import { PromptText } from "@/components/PromptText";
import { LEVEL } from "@/lib/when";
import { BookmarkButton } from "@/components/BookmarkButton";
import { questionKey } from "@/lib/bookmarkStore";
import { ANSWER_LANGUAGE_LABEL, ANSWER_PLACEHOLDER } from "@/lib/prefs";
import { useAnswerLanguage } from "@/lib/profileStore";

/** One question with an answer box, shared by Review practice and Timed quiz. */
export function QuestionBody({
  question,
  answer,
  onAnswer,
  disabled,
  tag,
  actions,
  rows = 6,
}: {
  question: Question;
  answer: string;
  onAnswer: (v: string) => void;
  disabled?: boolean;
  tag?: ReactNode;
  actions?: ReactNode;
  rows?: number;
}) {
  const level = LEVEL[question.difficulty] ?? 1;
  const answerLang = useAnswerLanguage();
  const blank = question.kind === "fill_blank";
  return (
    <article className="card q-enter" data-question-id={question.id} data-testid="question-body">
      <div className="flex flex-wrap items-center gap-2 border-b border-ink-700 px-4 py-3 sm:px-6">
        {tag}
        <span className="chip text-ink-100">{question.domain_name}</span>
        <span className="chip uppercase">{question.language}</span>
        <span className="chip gap-1.5" title={question.difficulty}>
          {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
          <span className="ml-1">{question.difficulty}</span>
        </span>
        {blank && <span className="chip border-accent text-accent">Missing code</span>}
        <BookmarkButton itemKey={questionKey(question.id)} className="ml-auto" />
      </div>
      <div className="grid gap-6 p-4 sm:p-6 lg:grid-cols-2">
        <div className="min-w-0 space-y-4">
          <h2 className="font-display text-2xl font-semibold leading-tight text-ink-50" data-testid="question-title">{question.title}</h2>
          <CodeBlock code={question.code} language={question.language} />
        </div>
        <div className="flex min-w-0 flex-col gap-4">
          <PromptText prompt={question.prompt} />
          <label className="flex flex-col gap-2">
            <span className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="label">{blank ? "The missing code" : "Your answer, in your own words"}</span>
              <span className="font-mono text-[11px] text-ink-500" lang="fil">
                {answerLang === "en" ? "English · Filipino · Taglish" : `${ANSWER_LANGUAGE_LABEL[answerLang]} · or English`}
              </span>
            </span>
            <textarea
              value={answer}
              onChange={(e) => onAnswer(e.target.value)}
              rows={blank ? 3 : rows}
              disabled={disabled}
              placeholder={blank ? "e.g. i += 1" : ANSWER_PLACEHOLDER[answerLang].short}
              className="input font-mono text-[13px] leading-6"
              data-testid="answer"
            />
          </label>
          {actions}
        </div>
      </div>
    </article>
  );
}
