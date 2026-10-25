"use client";

import { useEffect, useState } from "react";
import type { Question } from "@/lib/api";

const KEY = "vexalith_how_to_open";

/**
 * Per-question "How to answer" box. What to answer is already in the prompt's "Your task" line,
 * so this only adds what to look for (and, for fill-in questions, what counts as right).
 */
export function HowToAnswer({ question }: { question: Question }) {
  const [open, setOpen] = useState(true);
  useEffect(() => {
    setOpen(localStorage.getItem(KEY) !== "0");
  }, []);
  const kind = question.kind === "fill_blank" ? "fill" : question.language === "general" ? "prose" : "explain";
  const title = kind === "fill" ? "Fill in the missing code" : kind === "prose" ? "Solve and explain" : "Explain in your own words";
  return (
    <details
      className="border border-ink-700 bg-ink-900/60 px-4 py-3"
      open={open}
      onToggle={(e) => {
        const o = (e.currentTarget as HTMLDetailsElement).open;
        setOpen(o);
        localStorage.setItem(KEY, o ? "1" : "0");
      }}
      data-testid="how-to-answer"
      data-kind={kind}
    >
      <summary className="cursor-pointer font-mono text-[12px] uppercase tracking-wider text-ink-200">
        How to answer · <span className="text-accent">{title}</span>
      </summary>
      {question.guide && (
        <dl className="mt-3 space-y-1.5 text-sm">
          <div>
            <dt className="label inline">What to look for · </dt>
            <dd className="inline text-ink-300">{question.guide.look_for}</dd>
          </div>
          {question.guide.good_answer && (
            <div>
              <dt className="label inline">What counts · </dt>
              <dd className="inline text-ink-300">{question.guide.good_answer}</dd>
            </div>
          )}
        </dl>
      )}
    </details>
  );
}
