"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { loadUser, saveUser, clearUser, type StoredUser } from "@/lib/storage";

export default function HomePage() {
  const [user, setUser] = useState<StoredUser | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<string>("…");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setUser(loadUser());
    api
      .health()
      .then((h) => {
        const provider = (h.details?.provider as string) || "?";
        setHealth(
          `${h.status} · provider=${provider} · llm=${h.llm_configured} · db=${h.database}`
        );
      })
      .catch(() => setHealth("backend unreachable"));
  }, []);

  async function start() {
    setError(null);
    setBusy(true);
    try {
      const u = await api.createUser(name.trim());
      const stored = { id: u.id, display_name: u.display_name };
      saveUser(stored);
      setUser(stored);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create user");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    clearUser();
    setUser(null);
    setName("");
  }

  return (
    <div className="space-y-10">
      <section className="space-y-4">
        <p className="text-xs uppercase tracking-[0.2em] text-accent">Portfolio MVP</p>
        <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-ink-50 sm:text-5xl">
          Adaptive Learning for{" "}
          <span className="text-accent">Critical Thinking</span>
        </h1>
        <p className="max-w-2xl text-ink-300 leading-relaxed">
          Work through realistic scenarios, write open-ended answers, and get explainable
          feedback on logical fallacies and reasoning gaps. The next item adapts to your
          weakest skill domain using an Elo-style mastery model.
        </p>
        <p className="text-xs text-ink-500 font-mono">{health}</p>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-ink-700 bg-ink-900/50 p-6 space-y-4">
          <h2 className="text-lg font-medium text-ink-50">Get started</h2>
          {user ? (
            <div className="space-y-3">
              <p className="text-sm text-ink-300">
                Signed in as{" "}
                <span className="font-semibold text-accent-soft">{user.display_name}</span>{" "}
                <span className="text-ink-500">(id {user.id})</span>
              </p>
              <div className="flex flex-wrap gap-2">
                <Link
                  href="/practice"
                  className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-ink-950 hover:brightness-110"
                >
                  Start practicing →
                </Link>
                <Link
                  href="/progress"
                  className="rounded-lg border border-ink-600 px-4 py-2 text-sm text-ink-200 hover:bg-ink-800"
                >
                  View progress
                </Link>
                <button
                  type="button"
                  onClick={reset}
                  className="rounded-lg px-3 py-2 text-sm text-ink-400 hover:text-ink-200"
                >
                  Switch user
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <label className="block text-sm text-ink-300">
                Display name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. alex"
                  className="mt-1 w-full rounded-lg border border-ink-600 bg-ink-950 px-3 py-2 text-ink-50 outline-none focus:border-accent"
                />
              </label>
              {error && <p className="text-sm text-rose-300">{error}</p>}
              <button
                type="button"
                disabled={!name.trim() || busy}
                onClick={start}
                className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-ink-950 disabled:opacity-40 hover:brightness-110"
              >
                {busy ? "Creating…" : "Create learner profile"}
              </button>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-ink-700 bg-ink-900/50 p-6 space-y-3 text-sm text-ink-300">
          <h2 className="text-lg font-medium text-ink-50">How it works</h2>
          <ol className="list-decimal space-y-2 pl-5">
            <li>Five skill domains: argument analysis, fallacy detection, evidence, assumptions, causal reasoning.</li>
            <li>Feedback via <strong className="text-ink-100">xAI Grok</strong> when configured; otherwise Hugging Face zero-shot or a heuristic fallback.</li>
            <li>Mastery updates after each answer; the next question targets your weakest domain at a matched difficulty.</li>
          </ol>
        </div>
      </section>
    </div>
  );
}
