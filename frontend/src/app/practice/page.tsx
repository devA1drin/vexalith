"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, type Question, type FeedbackPayload } from "@/lib/api";
import { loadUser } from "@/lib/storage";
import { FeedbackCard } from "@/components/FeedbackCard";

export default function PracticePage() {
  const [userId, setUserId] = useState<number | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingQ, setLoadingQ] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const u = loadUser();
    setUserId(u?.id ?? null);
  }, []);

  const loadQuestion = useCallback(async (uid: number) => {
    setLoadingQ(true);
    setError(null);
    setFeedback(null);
    setAnswer("");
    try {
      const q = await api.nextQuestion(uid);
      setQuestion(q);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load question");
    } finally {
      setLoadingQ(false);
    }
  }, []);

  useEffect(() => {
    if (userId != null) loadQuestion(userId);
  }, [userId, loadQuestion]);

  async function onSubmit() {
    if (!userId || !question) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.submitResponse(userId, question.id, answer);
      setFeedback(res.feedback);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submit failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (userId == null) {
    return (
      <div className="rounded-xl border border-ink-700 bg-ink-900/50 p-8 text-center space-y-3">
        <p className="text-ink-300">Create a learner profile on the home page first.</p>
        <Link href="/" className="text-accent hover:underline">
          ← Home
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-ink-50">Practice</h1>
        <button
          type="button"
          onClick={() => userId && loadQuestion(userId)}
          disabled={loadingQ}
          className="rounded-lg border border-ink-600 px-3 py-1.5 text-sm text-ink-200 hover:bg-ink-800 disabled:opacity-40"
        >
          {loadingQ ? "Loading…" : "Skip / next"}
        </button>
      </div>

      {error && (
        <p className="rounded-lg border border-rose-800 bg-rose-950/40 px-3 py-2 text-sm text-rose-200">
          {error}
        </p>
      )}

      {question && (
        <article className="space-y-4 rounded-xl border border-ink-700 bg-ink-900/50 p-6">
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="rounded-full bg-ink-800 px-2.5 py-1 text-ink-200">
              {question.domain_name}
            </span>
            <span className="rounded-full bg-ink-800 px-2.5 py-1 capitalize text-accent-soft">
              {question.difficulty}
            </span>
          </div>
          <h2 className="text-xl font-medium text-ink-50">{question.title}</h2>
          <div>
            <h3 className="mb-1 text-xs uppercase tracking-wide text-ink-500">Scenario</h3>
            <p className="prose-scenario">{question.scenario}</p>
          </div>
          <div>
            <h3 className="mb-1 text-xs uppercase tracking-wide text-ink-500">Your task</h3>
            <p className="text-ink-100 font-medium">{question.prompt}</p>
          </div>

          <label className="block space-y-2">
            <span className="text-sm text-ink-300">Your answer</span>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={8}
              disabled={!!feedback}
              placeholder="Write a reasoned analysis (at least a few sentences)…"
              className="w-full rounded-lg border border-ink-600 bg-ink-950 px-3 py-2 text-sm text-ink-50 outline-none focus:border-accent disabled:opacity-60"
            />
          </label>

          {!feedback ? (
            <button
              type="button"
              onClick={onSubmit}
              disabled={answer.trim().length < 10 || submitting}
              className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-ink-950 disabled:opacity-40 hover:brightness-110"
            >
              {submitting ? "Analyzing…" : "Submit for feedback"}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => userId && loadQuestion(userId)}
              className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-ink-950 hover:brightness-110"
            >
              Next question →
            </button>
          )}
        </article>
      )}

      {feedback && <FeedbackCard feedback={feedback} />}
    </div>
  );
}
