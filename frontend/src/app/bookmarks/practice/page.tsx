"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type Bookmark, type BookmarkFilters, type FeedbackPayload, type Question } from "@/lib/api";
import { FeedbackCard } from "@/components/FeedbackCard";
import { QuestionBody } from "@/components/QuestionBody";
import { announceXp } from "@/lib/xp";
import { bookmarkQuery, readBookmarkFilters } from "@/lib/bookmarkFilters";

/** Go through saved questions one by one, graded exactly like Practice. */
export default function PracticeBookmarksPage() {
  const [filters, setFilters] = useState<BookmarkFilters>({});
  const [queue, setQueue] = useState<Bookmark[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [tally, setTally] = useState({ right: 0, tried: 0 });
  const [busy, setBusy] = useState<"load" | "submit" | null>("load");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const start = new URLSearchParams(window.location.search).get("start");
    const f = readBookmarkFilters(window.location.search);
    setFilters(f);
    api.bookmarks({ ...f, kind: "question" }).then((r) => {
      const items = r.items.filter((i) => i.kind === "question");
      const first = items.findIndex((i) => i.key === start);
      if (first > 0) items.unshift(...items.splice(first, 1));
      setQueue(items);
      if (!items.length) setBusy(null);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/bookmarks/practice";
      else setError(e instanceof Error ? e.message : "Couldn't load your bookmarks.");
      setBusy(null);
    });
  }, []);

  const item = queue?.[idx] ?? null;

  const open = useCallback(async (b: Bookmark) => {
    setBusy("load");
    setFeedback(null);
    setAnswer("");
    setQuestion(null);
    try {
      setQuestion(await api.question(b.id as number));
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
    if (!question) return;
    setBusy("submit");
    setError(null);
    try {
      const res = await api.submitResponse(question.id, answer);
      setFeedback(res.feedback);
      setTally((t) => ({ right: t.right + (res.feedback.verdict === "correct" ? 1 : 0), tried: t.tried + 1 }));
      announceXp();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't grade that answer.");
    } finally {
      setBusy(null);
    }
  };

  const total = queue?.length ?? 0;
  const done = queue !== null && idx >= total;
  const back = `/bookmarks${bookmarkQuery(filters)}`;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">Bookmarks · Practice</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Your saved questions.</h1>
        </div>
        <Link href={back} className="btn-ghost">← Back to Bookmarks</Link>
      </div>

      {total > 0 && !done && (
        <div className="space-y-2" data-testid="bookmark-progress">
          <div className="flex flex-wrap items-baseline justify-between gap-2 font-mono text-[12px] text-ink-400">
            <span><span className="text-ink-50">{idx + 1}</span> of {total}</span>
            <span>{tally.right} right</span>
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
          <h2 className="font-display text-2xl font-semibold text-ink-50">No saved questions here.</h2>
          <p className="text-[14px] text-ink-300">Nothing you saved matches these filters. Saved coding exercises open from the Bookmarks page.</p>
          <Link href={back} className="btn-ghost">Back to Bookmarks</Link>
        </div>
      )}

      {item && !done && (
        <>
          {item.note && (
            <p className="border-l-2 border-accent/60 pl-3 text-[14px] text-ink-200" data-testid="practice-note">
              <span className="text-ink-500">Your note: </span>{item.note}
            </p>
          )}
          {question ? (
            <QuestionBody
              key={question.id}
              question={question}
              answer={answer}
              onAnswer={setAnswer}
              disabled={!!feedback || busy === "submit"}
              actions={
                <div className="flex flex-wrap items-center gap-3">
                  {!feedback ? (
                    <>
                      <button type="button" className="btn-primary" onClick={submit} disabled={!answer.trim() || busy !== null} data-testid="submit">
                        {busy === "submit" ? "Checking…" : <>Check <span className="btn-arrow">→</span></>}
                      </button>
                      <button type="button" className="btn-ghost" onClick={() => setIdx((i) => i + 1)} disabled={busy !== null}>
                        Skip ↷
                      </button>
                    </>
                  ) : (
                    <button type="button" className="btn-primary" onClick={() => setIdx((i) => i + 1)} data-testid="next">
                      {idx + 1 < total ? <>Next <span className="btn-arrow">→</span></> : <>See summary <span className="btn-arrow">→</span></>}
                    </button>
                  )}
                </div>
              }
            />
          ) : (
            <div className="card h-64 animate-pulse" />
          )}
          {feedback && <FeedbackCard feedback={feedback} />}
        </>
      )}

      {done && total > 0 && (
        <div className="card space-y-4 p-6" data-testid="bookmarks-summary">
          <p className="label">Round finished</p>
          <h2 className="font-display text-3xl font-bold text-ink-50">{tally.right} of {tally.tried || total} right</h2>
          <p className="max-w-xl text-[14px] text-ink-300">
            Your bookmarks stay saved until you remove them. Anything you missed also shows up in Review mistakes.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href={back} className="btn-primary">Back to Bookmarks <span className="btn-arrow">→</span></Link>
            <Link href="/review" className="btn-ghost">Review mistakes</Link>
          </div>
        </div>
      )}
    </div>
  );
}
