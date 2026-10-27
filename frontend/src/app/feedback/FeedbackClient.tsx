"use client";

import { Avatar } from "@/components/Avatar";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type FeedbackCategory, type MyFeedback, type PublicFeedback } from "@/lib/api";

const CATEGORIES: { id: FeedbackCategory; label: string }[] = [
  { id: "bug", label: "Bug" },
  { id: "feature_request", label: "Feature request" },
  { id: "question_content", label: "Question content" },
  { id: "other", label: "Other" },
];
const LABEL = Object.fromEntries(CATEGORIES.map((c) => [c.id, c.label])) as Record<string, string>;
const MAX = 2000;

/** 1–5 rating as segmented blocks (keyboard: arrows within the radiogroup, or Tab + Enter). */
function Rating({ value, onChange }: { value: number; onChange?: (v: number) => void }) {
  if (!onChange) {
    return (
      <span className="inline-flex items-center gap-[3px]" aria-label={`${value} out of 5`} role="img">
        {[1, 2, 3, 4, 5].map((n) => <span key={n} className={`h-2 w-3 ${n <= value ? "bg-accent" : "bg-ink-700"}`} />)}
        <span className="ml-1.5 font-mono text-[11px] text-ink-400">{value}/5</span>
      </span>
    );
  }
  return (
    <div className="flex gap-1" role="radiogroup" aria-label="Rating">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          role="radio"
          aria-checked={value === n}
          aria-label={`${n} of 5`}
          onClick={() => onChange(n)}
          data-star={n}
          className={`group flex h-10 w-12 flex-col items-center justify-center border font-mono text-[12px] transition-colors ${
            n <= value ? "border-accent bg-accent text-ink-950" : "border-ink-600 text-ink-300 hover:border-accent hover:text-accent"
          }`}
        >
          {n}
        </button>
      ))}
      <span className="ml-2 self-center font-mono text-[11px] uppercase tracking-wider text-ink-400">
        {["", "broken", "rough", "okay", "good", "excellent"][value]}
      </span>
    </div>
  );
}

const fmt = (iso: string) => new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });

export function FeedbackClient({ signedIn, providers }: { signedIn: boolean; providers: string[] }) {
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState<FeedbackCategory>("feature_request");
  const [message, setMessage] = useState("");
  const [context, setContext] = useState("");
  const [status, setStatus] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [mine, setMine] = useState<MyFeedback[]>([]);
  const [wall, setWall] = useState<PublicFeedback[] | null>(null);

  const refresh = useCallback(() => {
    api.recentFeedback().then(setWall).catch(() => setWall([]));
    if (signedIn) api.myFeedback().then(setMine).catch(() => setMine([]));
  }, [signedIn]);

  useEffect(refresh, [refresh]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (rating < 1) return setStatus({ ok: false, text: "Please choose a rating." });
    setBusy(true);
    setStatus(null);
    try {
      await api.submitFeedback({ rating, category, message: message.trim(), page_context: context.trim() || null });
      setStatus({ ok: true, text: "Thanks! Your feedback was submitted." });
      setMessage("");
      setContext("");
      setRating(0);
      refresh();
    } catch (err) {
      setStatus({ ok: false, text: err instanceof Error ? err.message : "Submission failed" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-5">
      <div className="space-y-6 lg:col-span-3">
        {signedIn ? (
          <form onSubmit={submit} className="card space-y-5 p-6" data-testid="feedback-form">
            <div className="space-y-2">
              <span className="label">Rating</span>
              <Rating value={rating} onChange={setRating} />
            </div>
            <div className="space-y-2">
              <span className="label">Category</span>
              <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Category">
                {CATEGORIES.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setCategory(c.id)}
                    role="radio"
                    aria-checked={category === c.id}
                    className={`border px-3 py-1.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${
                      category === c.id ? "border-accent text-accent" : "border-ink-600 text-ink-300 hover:border-ink-400 hover:text-ink-50"
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>
            <label className="block space-y-2">
              <span className="label">Message</span>
              <textarea
                className="input"
                rows={5}
                maxLength={MAX}
                required
                minLength={5}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="What worked, what didn't, what should we build next?"
              />
              <span className={`block text-right font-mono text-[11px] ${message.length > MAX * 0.9 ? "text-signal" : "text-ink-500"}`}>{message.length}/{MAX}</span>
            </label>
            <label className="block space-y-2">
              <span className="label">Page or context (optional)</span>
              <input className="input" maxLength={300} value={context} onChange={(e) => setContext(e.target.value)} placeholder="e.g. /practice — 'Two-sum' question" />
            </label>
            {status && (
              <p role="status" className={`border-l-2 pl-3 text-sm ${status.ok ? "border-accent text-accent-soft" : "border-signal text-signal-soft"}`}>
                {status.text}
              </p>
            )}
            <button type="submit" className="btn-primary" disabled={busy || message.trim().length < 5}>
              {busy ? "Sending…" : "Submit feedback"}
            </button>
          </form>
        ) : (
          <div className="card space-y-4 p-6" data-testid="feedback-signin">
            <div className="label text-signal">auth required</div>
            <p className="font-display text-xl font-semibold text-ink-50">Sign in to send feedback.</p>
            <p className="text-sm text-ink-400">
              {providers.length ? `Use ${providers.join(" or ")} — it takes a few seconds.` : "GitHub and Google sign-in are being set up. Reading the wall is open to everyone."}
            </p>
            <Link href="/login?callbackUrl=/feedback" className="btn-primary">Sign in <span className="btn-arrow">→</span></Link>
          </div>
        )}

        {signedIn && (
          <section className="space-y-3">
            <h2 className="label border-b border-ink-700 pb-2 text-ink-200">Your submissions</h2>
            {mine.length === 0 ? (
              <p className="text-sm text-ink-500">Nothing yet.</p>
            ) : (
              <ul className="space-y-3">
                {mine.map((f) => (
                  <li key={f.id} className="card p-4">
                    <div className="flex items-center justify-between gap-2">
                      <Rating value={f.rating} />
                      <span className="chip">{LABEL[f.category]}</span>
                    </div>
                    <p className="mt-2 whitespace-pre-wrap text-sm text-ink-100">{f.message}</p>
                    <p className="mt-2 text-xs text-ink-500">{fmt(f.created_at)}{f.page_context ? ` · ${f.page_context}` : ""}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </div>

      <aside className="space-y-3 lg:col-span-2">
        <h2 className="label border-b border-ink-700 pb-2 text-ink-200">Recent feedback</h2>
        {wall === null ? (
          <div className="card h-32 animate-pulse" />
        ) : wall.length === 0 ? (
          <p className="text-sm text-ink-500">No feedback yet — be the first!</p>
        ) : (
          <ul className="space-y-3" data-testid="feedback-wall">
            {wall.map((f) => (
              <li key={f.id} className="card p-4">
                <div className="flex items-center gap-2">
                  <Avatar mark={f.author_avatar ?? (f.author_avatar_url ? "photo" : "initials-ink")} name={f.author_name} photoUrl={f.author_avatar_url} size={28} />
                  <span className="truncate text-sm font-medium text-ink-100">{f.author_name}</span>
                  <span className="chip ml-auto">{LABEL[f.category]}</span>
                </div>
                <div className="mt-3"><Rating value={f.rating} /></div>
                <p className="mt-1 whitespace-pre-wrap text-sm text-ink-200">{f.message}</p>
                <p className="mt-2 text-xs text-ink-500">{fmt(f.created_at)}</p>
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  );
}
