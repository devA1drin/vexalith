"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type DailyMeOut, type DailyOut } from "@/lib/api";

const LANG: Record<string, string> = {
  python: "Python", javascript: "JavaScript", php: "PHP", cpp: "C++", java: "Java", html: "HTML", css: "CSS", general: "General",
};
const LEVEL_N: Record<string, number> = { beginner: 1, intermediate: 2, advanced: 3 };

function useCountdown(target: string | undefined) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(t);
  }, []);
  if (!target) return "";
  const ms = Math.max(0, new Date(target).getTime() - now);
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return `${h}h ${String(m).padStart(2, "0")}m`;
}

function prettyDate(iso: string) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
}

/** Loads today's challenge: personal status when signed in, the public summary otherwise. */
export function useDaily(signedIn: boolean) {
  const [data, setData] = useState<DailyOut | DailyMeOut | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const load = signedIn
      ? api.dailyMe().catch((e) => (e instanceof ApiError && e.status === 401 ? api.daily() : Promise.reject(e)))
      : api.daily();
    load.then(setData).catch(() => setFailed(true));
  }, [signedIn]);
  return { data, failed };
}

export function DailyChallengeCard({ signedIn, full = false }: { signedIn: boolean; full?: boolean }) {
  const { data, failed } = useDaily(signedIn);
  const left = useCountdown(data?.resets_at);
  if (failed) return null;
  if (!data) return <div className="card h-44 animate-pulse" aria-hidden="true" />;

  const me = "completed" in data ? data : null;
  const level = LEVEL_N[data.difficulty] ?? 1;
  const href = `/practice?language=${data.language}&question=${data.question_id}`;
  const cta = signedIn ? href : `/login?callbackUrl=${encodeURIComponent(href)}`;

  return (
    <section className="card relative overflow-hidden" data-testid="daily-card" aria-labelledby="daily-h">
      <span aria-hidden="true" className="absolute inset-y-0 left-0 w-1 bg-accent" />
      <div className="grid gap-px bg-ink-800 md:grid-cols-[1fr_17rem]">
        <div className="bg-ink-900 p-5 pl-6 sm:p-6 sm:pl-7">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="label">
              <span className="text-accent">Daily challenge</span> · {prettyDate(data.date)} · Manila time
            </p>
            <span className="font-mono text-[11px] text-ink-500">new one in {left}</span>
          </div>
          <h2 id="daily-h" className="mt-3 font-display text-2xl font-semibold leading-tight text-ink-50 sm:text-3xl">{data.title}</h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="chip text-ink-100">{LANG[data.language] ?? data.language}</span>
            <span className="chip">{data.domain_name}</span>
            <span className="chip gap-1.5">
              {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
              <span className="ml-1">{data.difficulty}</span>
            </span>
            {data.kind === "fill_blank" && <span className="chip border-accent text-accent">Missing code</span>}
          </div>
          {/* The daily page explains this in its "how it works" cards, so the sentence is only shown on the home page. */}
          {!full && (
            <p className="mt-4 max-w-xl text-sm text-ink-400">
              One question a day, the same for everyone. It changes at midnight in Manila (UTC+8), rotating through every language and skill.
            </p>
          )}
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Link href={cta} className={me?.completed ? "btn-ghost" : "btn-primary"} data-testid="daily-start">
              {me?.completed ? "Try it again" : signedIn ? "Start today's challenge" : "Sign in to play"} <span className="btn-arrow">→</span>
            </Link>
            {!full && <Link href="/daily" className="font-mono text-[12px] uppercase tracking-wider text-ink-300 hover:text-ink-50">Streak &amp; history</Link>}
          </div>
        </div>
        <div className="flex flex-col justify-between gap-4 bg-ink-900 p-5 sm:p-6">
          {me ? (
            <>
              <div>
                <div className="label">Today</div>
                {me.completed ? (
                  <div className="mt-1 flex items-baseline gap-2" data-testid="daily-done">
                    <span className="font-display text-2xl font-bold text-accent">Done</span>
                    <span className="font-mono text-sm text-ink-300">{Math.round((me.score ?? 0) * 100)}/100</span>
                  </div>
                ) : (
                  <div className="mt-1 font-display text-2xl font-bold text-ink-50">Not yet</div>
                )}
              </div>
              <div className="grid grid-cols-2 gap-px border border-ink-700 bg-ink-700">
                <div className="bg-ink-950 p-3">
                  <div className="label">Streak</div>
                  <div className="mt-1 font-display text-3xl font-bold text-ink-50" data-testid="daily-streak">{me.current_streak}<span className="ml-1 text-sm font-normal text-ink-400">{me.current_streak === 1 ? "day" : "days"}</span></div>
                </div>
                <div className="bg-ink-950 p-3">
                  <div className="label">Best</div>
                  <div className="mt-1 font-display text-3xl font-bold text-ink-50">{me.best_streak}</div>
                </div>
              </div>
              <DayStrip days={me.last_days} />
            </>
          ) : (
            <p className="text-sm text-ink-300">Sign in to keep a streak: answer the daily challenge on consecutive days and see your best run on the progress page.</p>
          )}
        </div>
      </div>
    </section>
  );
}

export function DayStrip({ days }: { days: { date: string; done: boolean; score: number | null }[] }) {
  return (
    <div>
      <div className="label mb-1.5">Last {days.length} days</div>
      <div className="flex gap-1" role="list" aria-label="Daily challenges completed in the last days">
        {days.map((d, i) => (
          <span
            key={d.date}
            role="listitem"
            title={`${prettyDate(d.date)}: ${d.done ? `done (${Math.round((d.score ?? 0) * 100)}/100)` : "missed"}`}
            className={`h-4 flex-1 border ${d.done ? "border-accent bg-accent" : "border-ink-700 bg-ink-950"} ${i === days.length - 1 ? "outline outline-1 outline-offset-1 outline-ink-500" : ""}`}
          />
        ))}
      </div>
    </div>
  );
}
