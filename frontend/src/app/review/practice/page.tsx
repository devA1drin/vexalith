"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, ApiError, type FeedbackPayload, type Question, type ReviewItem } from "@/lib/api";
import { FeedbackCard } from "@/components/FeedbackCard";
import { QuestionBody } from "@/components/QuestionBody";
import { announceXp } from "@/lib/xp";
import { filtersQuery, readFilters } from "@/lib/reviewFilters";
import type { ReviewFilters } from "@/lib/api";

type Outcome = { kind: "fixed" | "stuck" | "still"; xp: number };

export default function PracticeMistakesPage() {
  const [filters, setFilters] = useState<ReviewFilters>({});
  const [queue, setQueue] = useState<ReviewItem[] | null>(null);
  const [fixXp, setFixXp] = useState(5);
  const [idx, setIdx] = useState(0);
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [tally, setTally] = useState({ fixed: 0, xp: 0, tried: 0 });
  const [busy, setBusy] = useState<"load" | "submit" | null>("load");
  const [error, setError] = useState<string | null>(null);
  const fixesRef = useRef(0);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const f = { ...readFilters(window.location.search), kind: "question" as const };
    const start = q.get("start");
    setFilters(f);
    api.review(f).then((r) => {
      const items = r.items.filter((i) => i.kind === "question");
      const first = items.findIndex((i) => i.key === start);
      if (first > 0) items.unshift(...items.splice(first, 1));
      fixesRef.current = r.fixes;
      setFixXp(r.rules.fix_xp);
      setQueue(items);
      if (!items.length) setBusy(null);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/review/practice";
      else setError(e instanceof Error ? e.message : "Couldn't load your mistakes.");
      setBusy(null);
    });
  }, []);

  const item = queue?.[idx] ?? null;

  const open = useCallback(async (it: ReviewItem) => {
    setBusy("load");
    setFeedback(null);
    setOutcome(null);
    setAnswer("");
    setQuestion(null);
    try {
      // Marks the start of a Review retry: only a right answer after this counts as a fix.
      await api.retryQuestion(it.id as number);
      setQuestion(await api.question(it.id as number));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't load that question.");
    } finally {
      setBusy(null);
    }
  }, []);

  useEffect(() => {
    if (item) open(item);
  }, [item, open]);

  const submit = async () => {
    if (!question || !item) return;
    setBusy("submit");
    setError(null);
    try {
      const res = await api.submitResponse(question.id, answer);
      setFeedback(res.feedback);
      const after = await api.review({});
      const gained = Math.max(0, after.fixes - fixesRef.current);
      fixesRef.current = after.fixes;
      const stillListed = after.items.some((i) => i.key === item.key);
      const kind: Outcome["kind"] = stillListed ? "still" : item.status === "check_again" ? "stuck" : "fixed";
      const xp = gained > 0 ? fixXp : 0;
      setOutcome({ kind, xp });
      setTally((t) => ({ fixed: t.fixed + (kind === "still" ? 0 : 1), xp: t.xp + xp, tried: t.tried + 1 }));
      announceXp();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't grade that answer.");
    } finally {
      setBusy(null);
    }
  };

  const total = queue?.length ?? 0;
  const done = queue !== null && idx >= total;
  const back = `/review${filtersQuery({ ...filters, kind: undefined })}`;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">01 · Practice · Review · Practice my mistakes</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">One more go.</h1>
        </div>
        <Link href={back} className="btn-ghost">← Back to Review</Link>
      </div>

      {total > 0 && !done && (
        <div className="space-y-2" data-testid="mistake-progress">
          <div className="flex flex-wrap items-baseline justify-between gap-2 font-mono text-[12px] text-ink-400">
            <span><span className="text-ink-50">{idx + 1}</span> of {total}</span>
            <span>{tally.fixed} fixed{tally.xp ? ` · +${tally.xp} XP` : ""}</span>
          </div>
          <div className="flex gap-1">
            {queue!.map((q, i) => (
              <span key={q.key} className={`h-1.5 flex-1 ${i < idx ? "bg-accent" : i === idx ? "bg-ink-300" : "bg-ink-800"}`} />
            ))}
          </div>
        </div>
      )}

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {queue === null && !error && <div className="card h-64 animate-pulse" />}
      {queue !== null && total === 0 && (
        <div className="card space-y-3 p-6">
          <h2 className="font-display text-2xl font-semibold text-ink-50">No questions to practise.</h2>
          <p className="text-[14px] text-ink-300">Nothing on your list matches these filters. Coding exercises are retried from the Review page.</p>
          <Link href={back} className="btn-ghost">Back to Review</Link>
        </div>
      )}

      {item && !done && (
        <>
          {item.last_answer && (
            <details className="panel px-4 py-3 text-[14px]" data-testid="last-time">
              <summary className="cursor-pointer font-mono text-[12px] uppercase tracking-wider text-ink-400">What you said last time</summary>
              <pre className="mt-2 whitespace-pre-wrap break-words font-mono text-[12px] leading-5 text-ink-300">{item.last_answer}</pre>
              {item.feedback && <p className="mt-2 text-ink-300"><span className="text-ink-500">What went wrong: </span>{item.feedback}</p>}
            </details>
          )}
          {question ? (
            <QuestionBody
              key={question.id}
              question={question}
              answer={answer}
              onAnswer={setAnswer}
              disabled={!!feedback || busy === "submit"}
              tag={
                item.status === "check_again" ? (
                  <span className="chip border-accent bg-accent text-ink-950">Check again</span>
                ) : (
                  <span className="chip border-signal text-signal">{item.reason_label}</span>
                )
              }
              actions={
                <div className="flex flex-wrap items-center gap-3">
                  {!feedback ? (
                    <>
                      <button type="button" className="btn-primary" onClick={submit} disabled={!answer.trim() || busy !== null} data-testid="submit">
                        {busy === "submit" ? "Checking…" : <>Check <span className="btn-arrow">→</span></>}
                      </button>
                      <button type="button" className="btn-ghost" onClick={() => setIdx((i) => i + 1)} disabled={busy !== null}>
                        Not now ↷
                      </button>
                    </>
                  ) : (
                    <button type="button" className="btn-primary" onClick={() => setIdx((i) => i + 1)} data-testid="next">
                      {idx + 1 < total ? <>Next mistake <span className="btn-arrow">→</span></> : <>See summary <span className="btn-arrow">→</span></>}
                    </button>
                  )}
                </div>
              }
            />
          ) : (
            <div className="card h-64 animate-pulse" />
          )}
          {outcome && <OutcomeBanner o={outcome} />}
          {feedback && <FeedbackCard feedback={feedback} />}
        </>
      )}

      {done && total > 0 && (
        <div className="card space-y-4 p-6" data-testid="mistakes-summary">
          <p className="label">Round finished</p>
          <h2 className="font-display text-3xl font-bold text-ink-50">
            {tally.fixed} of {tally.tried || total} fixed{tally.xp ? ` · +${tally.xp} XP` : ""}
          </h2>
          <p className="max-w-xl text-[14px] text-ink-300">
            Fixed questions come back once in a few days to check they stuck. Anything you missed stays on your list.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href={back} className="btn-primary">Back to Review <span className="btn-arrow">→</span></Link>
            <Link href="/quiz" className="btn-ghost">Try a timed quiz</Link>
          </div>
        </div>
      )}
    </div>
  );
}

function OutcomeBanner({ o }: { o: Outcome }) {
  if (o.kind === "still")
    return (
      <div role="status" className="rise flex flex-wrap items-center gap-3 border border-signal/60 bg-signal/10 px-4 py-3" data-testid="outcome-still">
        <span className="font-display text-lg font-semibold text-signal">Not yet.</span>
        <span className="text-[14px] text-ink-200">It stays on your list. Read the feedback below and try again later.</span>
      </div>
    );
  return (
    <div role="status" className="rise flex flex-wrap items-center gap-3 border border-accent bg-accent/10 px-4 py-3" data-testid="outcome-fixed">
      <span className="grid h-7 w-7 place-items-center bg-accent font-bold text-ink-950" aria-hidden="true">✓</span>
      <span className="font-display text-lg font-semibold text-accent">{o.kind === "stuck" ? "It stuck." : "Fixed."}</span>
      <span className="text-[14px] text-ink-200">
        {o.kind === "stuck" ? "Off your list for good." : "It leaves your list and comes back once in a few days."}
      </span>
      {o.xp > 0 && <span className="ml-auto font-mono text-[13px] font-semibold text-accent">+{o.xp} XP</span>}
    </div>
  );
}
