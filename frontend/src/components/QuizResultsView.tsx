"use client";

import { BookmarkButton } from "@/components/BookmarkButton";
import { questionKey } from "@/lib/bookmarkStore";
import Link from "next/link";
import type { QuizResults, QuizReviewRow } from "@/lib/api";
import { BadgeMark } from "@/components/BadgeMark";
import { CodeBlock } from "@/components/CodeBlock";
import { mmss } from "@/lib/when";

const STATUS: Record<QuizReviewRow["status"], [string, string, string]> = {
  correct: ["Right", "border-accent text-accent", "bg-accent"],
  partial: ["Partly right", "border-ink-300 text-ink-100", "bg-ink-300"],
  wrong: ["Wrong", "border-signal text-signal", "bg-signal"],
  unanswered: ["No answer", "border-ink-600 text-ink-400", "bg-ink-700"],
  skipped: ["Skipped", "border-ink-600 text-ink-400", "border border-dashed border-ink-500"],
};
const ENDED: Record<QuizResults["ended_by"], string> = { done: "You answered them all", time: "Time ran out", ended: "You ended it early" };

/** The score screen at the end of a timed quiz, with every question explained. */
export function QuizResultsView({ r }: { r: QuizResults }) {
  const pct = Math.round(r.score * 100);
  const again = `/quiz?scope=${r.scope}&value=${encodeURIComponent(r.scope_value)}&length=${r.length}&minutes=${Math.round(r.time_limit_s / 60)}${r.instant ? "&instant=1" : ""}`;
  return (
    <div className="space-y-8" data-testid="quiz-results">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">01 · Practice · Timed quiz · Results</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">{pct >= 80 ? "Sharp." : pct >= 50 ? "Getting there." : "Good practice."}</h1>
      </div>

      <section className="card overflow-hidden">
        <div className="grid gap-px bg-ink-700 md:grid-cols-[minmax(0,1.3fr)_minmax(0,2fr)]">
          <div className="bg-ink-950 p-5 sm:p-6">
            <div className="label">{r.scope_label}</div>
            <div className="mt-2 flex items-baseline gap-3">
              <span className={`font-display text-6xl font-bold tabular-nums ${pct >= 80 ? "text-accent" : "text-ink-50"}`} data-testid="quiz-score">
                {r.correct}<span className="text-ink-500">/{r.length}</span>
              </span>
              <span className="font-mono text-xl text-ink-300">{pct}%</span>
            </div>
            <div className="mt-3 flex gap-1" aria-hidden="true">
              {r.questions.map((q) => <span key={q.position} className={`h-2 flex-1 ${STATUS[q.status][2]}`} />)}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {r.new_best && <span className="chip border-accent bg-accent text-ink-950">New best</span>}
              {!r.new_best && r.best_before !== null && <span className="chip">Best so far {Math.round(r.best_before * 100)}%</span>}
              <span className="chip">{ENDED[r.ended_by]}</span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-px bg-ink-700">
            <Stat label="Time used" value={mmss(r.time_used_s)} sub={`of ${mmss(r.time_limit_s)}`} />
            <Stat label="XP earned" value={`+${r.xp}`} sub="no XP twice for a question" accent={r.xp > 0} />
            <Stat label="To Review" value={String(r.to_review)} sub={r.to_review ? "missed ones saved" : "nothing missed"} />
          </div>
        </div>
        {r.beat_the_clock && (
          <div className="flex flex-wrap items-center gap-4 border-t border-ink-700 bg-accent/5 px-5 py-4" data-testid="beat-the-clock">
            <BadgeMark id="beat-the-clock" group="review" earned size={48} />
            <div>
              <div className="font-display text-lg font-semibold text-accent">Beat the Clock</div>
              <div className="text-[13px] text-ink-300">80% or more on a quiz of 10 or more questions.</div>
            </div>
          </div>
        )}
      </section>

      <div className="flex flex-wrap gap-3">
        <Link href={again} className="btn-primary">Another quiz like this <span className="btn-arrow">→</span></Link>
        {r.to_review > 0 && <Link href="/review" className="btn-ghost" data-testid="to-review">Review {r.to_review} mistake{r.to_review === 1 ? "" : "s"}</Link>}
        <Link href="/quiz" className="btn-ghost">All quizzes</Link>
      </div>

      <section className="space-y-3">
        <h2 className="font-display text-2xl font-semibold text-ink-50">Question by question</h2>
        <ol className="space-y-2" data-testid="quiz-review">
          {r.questions.map((q) => <Row key={q.position} q={q} />)}
        </ol>
      </section>
    </div>
  );
}

function Stat({ label, value, sub, accent }: { label: string; value: string; sub: string; accent?: boolean }) {
  return (
    <div className="min-w-0 bg-ink-950 p-4 sm:p-5">
      <div className="label">{label}</div>
      <div className={`mt-1 font-display text-2xl font-bold tabular-nums sm:text-3xl ${accent ? "text-accent" : "text-ink-50"}`}>{value}</div>
      <div className="mt-0.5 font-mono text-[11px] leading-4 text-ink-500">{sub}</div>
    </div>
  );
}

function Row({ q }: { q: QuizReviewRow }) {
  const [word, tone] = STATUS[q.status];
  const right = q.kind === "fill_blank" && q.accepted_answers.length ? q.accepted_answers.join("  or  ") : q.reference_answer;
  return (
    <li>
      <details className="card group" open={q.status !== "correct"}>
        <summary className="flex cursor-pointer list-none flex-wrap items-center gap-x-3 gap-y-1 px-4 py-3 sm:px-5">
          <span className="font-mono text-[12px] text-ink-500">{String(q.position + 1).padStart(2, "0")}</span>
          <span className={`chip ${tone}`}>{word}</span>
          <span className="min-w-0 flex-1 basis-40 break-words font-display text-[16px] font-semibold text-ink-50">{q.title}</span>
          <span className="font-mono text-[11px] uppercase text-ink-500">{q.language} · {q.topic_name}</span>
          {/* Saving shouldn't open or close the row. */}
          <span onClick={(e) => e.preventDefault()}><BookmarkButton itemKey={questionKey(q.question_id)} compact /></span>
          <span className="text-ink-500 transition-transform group-open:rotate-90" aria-hidden="true">›</span>
        </summary>
        <div className="grid gap-4 border-t border-ink-800 p-4 sm:p-5 lg:grid-cols-2">
          <div className="min-w-0 space-y-3">
            <p className="text-[14px] leading-relaxed text-ink-300">{q.prompt}</p>
            {q.code && <CodeBlock code={q.code} language={q.language} />}
          </div>
          <div className="min-w-0 space-y-3 text-[14px]">
            <div>
              <div className="label mb-1">Your answer</div>
              {q.answer ? (
                <pre className="whitespace-pre-wrap break-words border border-ink-800 bg-ink-900 px-3 py-2 font-mono text-[12px] leading-5 text-ink-200">{q.answer}</pre>
              ) : (
                <p className="font-mono text-[12px] text-ink-500">{q.status === "skipped" ? "Skipped." : "No answer."}</p>
              )}
            </div>
            {q.status !== "correct" && q.feedback && (
              <div>
                <div className="label mb-1">What went wrong</div>
                <p className="leading-relaxed text-ink-200">{q.feedback}</p>
              </div>
            )}
            {right && (
              <div>
                <div className="label mb-1">{q.kind === "fill_blank" ? "The missing code" : "A good answer"}</div>
                <p className="break-words font-mono text-[12px] leading-5 text-accent">{right}</p>
              </div>
            )}
            {q.key_idea && (
              <div className="border-l-2 border-accent/60 pl-3">
                <div className="label mb-1">The idea</div>
                <p className="leading-relaxed text-ink-300">{q.key_idea}</p>
              </div>
            )}
          </div>
        </div>
      </details>
    </li>
  );
}
