"use client";

import { useEffect, useState } from "react";
import type { Question } from "@/lib/api";

const KEY = "vexalith_how_to_open";

const EXPLAIN_STEPS = [
  "Read the code (or problem) and the question above.",
  "Write your answer first, e.g. “It prints 5.”",
  "Then say why in 1-3 sentences, pointing at the lines that matter.",
];
const FILL_STEPS = [
  "Find the ? slot in the code. That's the missing piece.",
  "Type only the code that belongs there, e.g. i += 1",
  "Optional: add one short sentence on why it fits.",
];
const PROSE_STEPS = [
  "Read the problem carefully. There's no code to run here.",
  "Give your answer first, e.g. “The next number is 13.”",
  "Then show the steps or cases that prove it.",
];

/** Per-question "How to answer" guide: what to do, what to look for, and what a good answer contains. */
export function HowToAnswer({ question }: { question: Question }) {
  const [open, setOpen] = useState(true);
  useEffect(() => {
    setOpen(localStorage.getItem(KEY) !== "0");
  }, []);
  const kind = question.kind === "fill_blank" ? "fill" : question.language === "general" ? "prose" : "explain";
  const steps = kind === "fill" ? FILL_STEPS : kind === "prose" ? PROSE_STEPS : EXPLAIN_STEPS;
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
      <ol className="mt-3 space-y-1.5 text-sm text-ink-200">
        {steps.map((s, i) => (
          <li key={s} className="flex gap-2.5">
            <span className="font-mono text-[12px] text-accent">{i + 1}.</span>
            <span>{s}</span>
          </li>
        ))}
      </ol>
      {question.guide && (
        <dl className="mt-3 space-y-1.5 border-t border-ink-800 pt-3 text-sm">
          <div>
            <dt className="label inline">What to look for · </dt>
            <dd className="inline text-ink-300">{question.guide.look_for}</dd>
          </div>
          <div>
            <dt className="label inline">A good answer · </dt>
            <dd className="inline text-ink-300">{question.guide.good_answer}</dd>
          </div>
        </dl>
      )}
    </details>
  );
}
