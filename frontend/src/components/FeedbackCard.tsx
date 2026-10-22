"use client";

import type { FeedbackPayload } from "@/lib/api";
import { CountUp } from "@/components/CountUp";

const VERDICT = {
  correct: { label: "Correct", cls: "border-accent text-accent" },
  partially_correct: { label: "Partially correct", cls: "border-ink-300 text-ink-100" },
  incorrect: { label: "Not quite", cls: "border-signal text-signal" },
} as const;

function Meter({ label, value, delay }: { label: string; value: number; delay: number }) {
  const pct = Math.round(value * 100);
  return (
    <div>
      <div className="mb-1.5 flex justify-between font-mono text-[12px] uppercase tracking-wider">
        <span className="text-ink-300">{label}</span>
        <span className="text-ink-50"><CountUp to={pct} delay={delay} /></span>
      </div>
      <div className="h-1.5 bg-ink-800" role="meter" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
        <div className="bar-grow h-full bg-accent" style={{ width: `${pct}%`, ["--rd" as string]: `${delay}ms` }} />
      </div>
    </div>
  );
}

function Block({ title, tone, children, delay }: { title: string; tone: string; children: React.ReactNode; delay: number }) {
  return (
    <div className={`rise border-l-2 pl-4 ${tone}`} style={{ ["--rd" as string]: `${delay}ms` }}>
      <h4 className="label mb-2 !text-current">{title}</h4>
      {children}
    </div>
  );
}

export function FeedbackCard({ feedback }: { feedback: FeedbackPayload }) {
  const v = VERDICT[feedback.verdict] ?? VERDICT.partially_correct;
  const overall = Math.round(feedback.overall_score * 100);
  let d = 500;
  const next = () => (d += 90);
  return (
    <section className="card q-enter space-y-6 p-6" data-testid="feedback-card" aria-live="polite">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div className="space-y-2">
          <span className="label">Evaluation · {feedback.provider_used}</span>
          <div><span className={`inline-block border px-2.5 py-1 font-mono text-[12px] uppercase tracking-wider ${v.cls}`}>{v.label}</span></div>
        </div>
        <div className="font-display text-5xl font-bold leading-none text-ink-50">
          <CountUp to={overall} /><span className="text-2xl text-ink-500">/100</span>
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <Meter label="Correctness" value={feedback.correctness_score} delay={150} />
        <Meter label="Reasoning" value={feedback.reasoning_score} delay={300} />
      </div>

      <Explanation feedback={feedback} />

      {feedback.raw_explanation && <p className="rise text-[15px] leading-relaxed text-ink-200" style={{ ["--rd" as string]: "400ms" }}>{feedback.raw_explanation}</p>}

      {feedback.strengths.length > 0 && (
        <Block title="Held up" tone="border-accent text-accent" delay={next()}><List items={feedback.strengths} /></Block>
      )}
      {feedback.missed_concepts.length > 0 && (
        <Block title="Missed" tone="border-ink-300 text-ink-200" delay={next()}><List items={feedback.missed_concepts} /></Block>
      )}
      {feedback.misconceptions.length > 0 && (
        <Block title="Misconceptions" tone="border-signal text-signal" delay={next()}>
          <ul className="space-y-3">
            {feedback.misconceptions.map((m, i) => (
              <li key={i}>
                <div className="font-semibold text-ink-50">{m.name}</div>
                <p className="mt-0.5 text-sm text-ink-200">{m.explanation}</p>
                {m.evidence_span && <p className="mt-1 font-mono text-xs text-ink-400">you wrote: “{m.evidence_span}”</p>}
              </li>
            ))}
          </ul>
        </Block>
      )}
      {feedback.reasoning_gaps.length > 0 && (
        <Block title="Reasoning gaps" tone="border-ink-500 text-ink-300" delay={next()}>
          <ul className="space-y-3">
            {feedback.reasoning_gaps.map((g, i) => (
              <li key={i}>
                <p className="text-sm text-ink-100">{g.description}</p>
                <p className="mt-0.5 text-sm text-accent-soft">→ {g.how_to_improve}</p>
              </li>
            ))}
          </ul>
        </Block>
      )}
      {feedback.suggestions.length > 0 && (
        <Block title="Next steps" tone="border-ink-500 text-ink-300" delay={next()}><List items={feedback.suggestions} /></Block>
      )}
      {feedback.reference_answer && (
        <details className="group border border-ink-700 p-4" open={feedback.verdict !== "correct"} data-testid="model-answer">
          <summary className="cursor-pointer font-mono text-[12px] uppercase tracking-wider text-accent">Model answer</summary>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-ink-100">{feedback.reference_answer}</p>
        </details>
      )}
    </section>
  );
}

function List({ items }: { items: string[] }) {
  return (
    <ul className="space-y-1 text-sm text-ink-100">
      {items.map((s, i) => <li key={i} className="flex gap-2"><span className="text-ink-500">–</span><span>{s}</span></li>)}
    </ul>
  );
}

/**
 * Why the answer is right or wrong, for both question kinds: the verdict in
 * plain words, the key concept, the correct code for fill-in questions, and
 * every point a full answer covers (ticked when the grader saw it).
 */
function Explanation({ feedback }: { feedback: FeedbackPayload }) {
  const points = feedback.key_points ?? [];
  const accepted = feedback.accepted_answers ?? [];
  const covered = (label: string) => feedback.strengths.some((s) => s.toLowerCase().includes(label.toLowerCase()));
  const correct = feedback.verdict === "correct";
  const headline = correct
    ? "Why this is right"
    : feedback.verdict === "partially_correct"
      ? "Partly there. Here is what a full answer needs"
      : "Why this isn't right yet";
  if (!points.length && !accepted.length && !feedback.hints_used) return null;
  return (
    <div className="rise grid gap-5 border border-ink-700 bg-ink-950 p-5 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]" style={{ ["--rd" as string]: "350ms" }} data-testid="explanation">
      <div className="space-y-3">
        <h3 className={`label !text-current ${correct ? "text-accent" : "text-ink-100"}`}>{headline}</h3>
        {points[0] && (
          <p className="text-[15px] leading-relaxed text-ink-50">
            <span className="mr-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">Key concept</span>
            {points[0]}
          </p>
        )}
        {accepted.length > 0 && (
          <div>
            <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">{correct ? "Also accepted" : "Correct code for the blank"}</p>
            <div className="flex flex-wrap gap-2">
              {accepted.slice(0, 4).map((a) => (
                <code key={a} className="border border-accent/60 bg-accent/10 px-2 py-0.5 font-mono text-[13px] text-accent">{a}</code>
              ))}
            </div>
          </div>
        )}
        {!!feedback.hints_used && (
          <p className="font-mono text-[12px] text-ink-400">
            {feedback.hints_used} hint{feedback.hints_used > 1 ? "s" : ""} used · score −{Math.round((feedback.hint_penalty ?? 0) * 100)}%
          </p>
        )}
      </div>
      {points.length > 1 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">A full answer covers</p>
          <ul className="space-y-1.5 text-sm">
            {points.map((p) => {
              const ok = covered(p);
              return (
                <li key={p} className="grid grid-cols-[1.25rem_1fr] gap-1.5">
                  <span aria-hidden="true" className={ok ? "text-accent" : "text-ink-600"}>{ok ? "✓" : "○"}</span>
                  <span className={ok ? "text-ink-100" : "text-ink-300"}>{p}<span className="sr-only">{ok ? " (covered)" : " (not covered)"}</span></span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
