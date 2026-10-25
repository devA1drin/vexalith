"use client";

import { useEffect, useState } from "react";
import type { FeedbackPayload } from "@/lib/api";
import { CountUp } from "@/components/CountUp";
import { LABEL_LANG_KEY, LABELS, type LabelLang, type Labels } from "@/lib/feedbackLabels";

const VERDICT = {
  correct: "border-accent text-accent",
  partially_correct: "border-ink-300 text-ink-100",
  incorrect: "border-signal text-signal",
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
  const filipino = !!feedback.answer_language && feedback.answer_language !== "en";
  // Label language: the learner's saved choice, otherwise Filipino for Filipino/Taglish answers.
  const [lang, setLang] = useState<LabelLang>(filipino ? "fil" : "en");
  useEffect(() => {
    const saved = localStorage.getItem(LABEL_LANG_KEY);
    if (saved === "en" || saved === "fil") setLang(saved);
  }, []);
  const choose = (l: LabelLang) => {
    setLang(l);
    localStorage.setItem(LABEL_LANG_KEY, l);
  };
  const t = LABELS[lang];
  const vcls = VERDICT[feedback.verdict] ?? VERDICT.partially_correct;
  const vlabel = t[feedback.verdict] ?? t.partially_correct;
  const overall = Math.round(feedback.overall_score * 100);
  let d = 500;
  const next = () => (d += 90);
  // When the checklist is shown, it already says which points were covered and which are missing,
  // so notes that just restate a checklist point are left out.
  const points = feedback.key_points ?? [];
  const inChecklist = (text: string) => points.length > 1 && points.some((p) => text.toLowerCase().includes(p.toLowerCase()));
  const strengths = feedback.strengths.filter((s) => !inChecklist(s));
  const gaps = feedback.reasoning_gaps.filter((g) => !inChecklist(g.description));
  const suggestions = feedback.suggestions.filter((s) => !inChecklist(s));
  return (
    <section className="card q-enter space-y-6 p-6" data-testid="feedback-card" aria-live="polite">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div className="space-y-2">
          <span className="label">{t.evaluation} · {feedback.provider_used}</span>
          <div><span className={`inline-block border px-2.5 py-1 font-mono text-[12px] uppercase tracking-wider ${vcls}`} data-testid="verdict">{vlabel}</span></div>
        </div>
        <div className="flex items-end gap-5">
          <div className="flex items-center gap-2" role="radiogroup" aria-label="Feedback label language">
            <span className="label hidden sm:inline">{t.labelsIn}</span>
            <div className="grid grid-cols-2 gap-px border border-ink-700 bg-ink-700">
              {(["en", "fil"] as const).map((l) => (
                <button
                  key={l}
                  type="button"
                  role="radio"
                  aria-checked={lang === l}
                  onClick={() => choose(l)}
                  data-label-lang={l}
                  className={`px-2 py-1 font-mono text-[11px] uppercase tracking-wider transition-colors ${lang === l ? "bg-ink-100 text-ink-950" : "bg-ink-950 text-ink-300 hover:text-ink-50"}`}
                >
                  {l === "en" ? "English" : "Filipino"}
                </button>
              ))}
            </div>
          </div>
          <div className="font-display text-5xl font-bold leading-none text-ink-50">
            <CountUp to={overall} /><span className="text-2xl text-ink-500">/100</span>
          </div>
        </div>
      </div>

      {feedback.language_note && (
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 border-l-2 border-accent pl-3" data-testid="language-note" lang="fil">
          <span className="font-mono text-[11px] uppercase tracking-wider text-accent">{feedback.answer_language === "taglish" ? "Taglish" : "Filipino"}</span>
          <span className="text-sm text-ink-100">{feedback.language_note}</span>
          {lang === "fil" && t.contentNote && <span className="text-[12px] text-ink-400">{t.contentNote}</span>}
        </div>
      )}

      {feedback.daily_completed && (
        <div className="flex flex-wrap items-center justify-between gap-3 border border-accent bg-accent/10 px-4 py-3" data-testid="daily-complete">
          <span className="font-mono text-[12px] uppercase tracking-wider text-accent">{t.dailyDone}</span>
          <span className="text-sm text-ink-100">
            {t.streak}: <span className="font-semibold text-ink-50">{feedback.daily_streak ?? 1} {t.days(feedback.daily_streak ?? 1)}</span>
            <a href="/daily" className="ml-3 text-ink-300 underline-offset-2 hover:text-ink-50 hover:underline">{t.history}</a>
          </span>
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-2">
        <Meter label={t.correctness} value={feedback.correctness_score} delay={150} />
        <Meter label={t.reasoning} value={feedback.reasoning_score} delay={300} />
      </div>

      <Explanation feedback={feedback} t={t} />

      {feedback.raw_explanation && <p className="rise text-[15px] leading-relaxed text-ink-200" style={{ ["--rd" as string]: "400ms" }}>{feedback.raw_explanation}</p>}

      {strengths.length > 0 && (
        <Block title={t.heldUp} tone="border-accent text-accent" delay={next()}><List items={strengths} /></Block>
      )}
      {feedback.missed_concepts.length > 0 && !feedback.missed_concepts.every((m) => points.includes(m)) && (
        <Block title={t.missed} tone="border-ink-300 text-ink-200" delay={next()}><List items={feedback.missed_concepts} /></Block>
      )}
      {feedback.misconceptions.length > 0 && (
        <Block title={t.misconceptions} tone="border-signal text-signal" delay={next()}>
          <ul className="space-y-3">
            {feedback.misconceptions.map((m, i) => (
              <li key={i}>
                <div className="font-semibold text-ink-50">{m.name}</div>
                <p className="mt-0.5 text-sm text-ink-200">{m.explanation}</p>
                {m.evidence_span && <p className="mt-1 font-mono text-xs text-ink-400">{t.youWrote}: “{m.evidence_span}”</p>}
              </li>
            ))}
          </ul>
        </Block>
      )}
      {gaps.length > 0 && (
        <Block title={t.gaps} tone="border-ink-500 text-ink-300" delay={next()}>
          <ul className="space-y-3">
            {gaps.map((g, i) => (
              <li key={i}>
                <p className="text-sm text-ink-100">{g.description}</p>
                <p className="mt-0.5 text-sm text-accent-soft">→ {g.how_to_improve}</p>
              </li>
            ))}
          </ul>
        </Block>
      )}
      {suggestions.length > 0 && (
        <Block title={t.nextSteps} tone="border-ink-500 text-ink-300" delay={next()}><List items={suggestions} /></Block>
      )}
      {feedback.reference_answer && (
        <details className="group border border-ink-700 p-4" open={feedback.verdict !== "correct"} data-testid="model-answer">
          <summary className="cursor-pointer font-mono text-[12px] uppercase tracking-wider text-accent">{t.modelAnswer}</summary>
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
function Explanation({ feedback, t }: { feedback: FeedbackPayload; t: Labels }) {
  const points = feedback.key_points ?? [];
  const accepted = feedback.accepted_answers ?? [];
  const covered = (label: string) => feedback.strengths.some((s) => s.toLowerCase().includes(label.toLowerCase()));
  const correct = feedback.verdict === "correct";
  const headline = correct ? t.whyRight : feedback.verdict === "partially_correct" ? t.whyPartial : t.whyWrong;
  if (!points.length && !accepted.length && !feedback.hints_used) return null;
  return (
    <div className="rise grid gap-5 border border-ink-700 bg-ink-950 p-5 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]" style={{ ["--rd" as string]: "350ms" }} data-testid="explanation">
      <div className="space-y-3">
        <h3 className={`label !text-current ${correct ? "text-accent" : "text-ink-100"}`}>{headline}</h3>
        {points[0] && (
          <p className="text-[15px] leading-relaxed text-ink-50">
            <span className="mr-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">{t.keyConcept}</span>
            {points[0]}
          </p>
        )}
        {accepted.length > 0 && (
          <div>
            <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">{correct ? t.alsoAccepted : t.correctCode}</p>
            <div className="flex flex-wrap gap-2">
              {accepted.slice(0, 4).map((a) => (
                <code key={a} className="border border-accent/60 bg-accent/10 px-2 py-0.5 font-mono text-[13px] text-accent">{a}</code>
              ))}
            </div>
          </div>
        )}
        {!!feedback.hints_used && (
          <p className="font-mono text-[12px] text-ink-400">
            {t.hintsUsed(feedback.hints_used, Math.round((feedback.hint_penalty ?? 0) * 100))}
          </p>
        )}
      </div>
      {points.length > 1 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">{t.fullAnswer}</p>
          <ul className="space-y-1.5 text-sm">
            {points.map((p) => {
              const ok = covered(p);
              return (
                <li key={p} className="grid grid-cols-[1.25rem_1fr] gap-1.5">
                  <span aria-hidden="true" className={ok ? "text-accent" : "text-ink-600"}>{ok ? "✓" : "○"}</span>
                  <span className={ok ? "text-ink-100" : "text-ink-300"}>{p}<span className="sr-only">{ok ? t.covered : t.notCovered}</span></span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
