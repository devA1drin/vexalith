"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type FundamentalsStatus, type LanguageProgress, type ProgressOut, type RecentAttempt } from "@/lib/api";
import { MasteryChart } from "@/components/MasteryChart";
import { CountUp } from "@/components/CountUp";
import { Recommendations } from "@/components/Recommendations";
import { TrendChart } from "@/components/TrendChart";
import { PageIntro } from "@/components/PageIntro";
import { RanksTabs } from "@/components/RanksTabs";
import { ProgressLevel } from "@/components/ProgressLevel";

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.progress().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/progress";
      else setError(e instanceof Error ? e.message : "Failed");
    });
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">04 · Progress{data && ` · ${data.display_name}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Where your logic holds.</h1>
        </div>
        <Link href="/practice" className="btn-primary">Continue <span className="btn-arrow">→</span></Link>
      </div>
      <RanksTabs />
      <ProgressLevel />
      <PageIntro>
        <span className="text-ink-100">Mastery</span> (0-100) goes up when you answer a skill well and down a little when you
        miss, so the lowest bar is the best thing to practise next.
      </PageIntro>
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-48 animate-pulse" />}
      {data && data.total_responses === 0 && (
        <div className="card border-accent p-6" data-testid="progress-empty">
          <p className="label mb-2 text-accent">Welcome · nothing here yet</p>
          <h2 className="font-display text-2xl font-semibold text-ink-50">Answer your first question to see your progress.</h2>
          <ol className="mt-3 space-y-1 text-sm text-ink-300">
            <li>1. Go to Practice and pick a language (Python is a good start).</li>
            <li>2. Choose Beginner if you&apos;re new, or leave it on Adaptive.</li>
            <li>3. Answer a few questions. Your charts and suggestions show up here right away.</li>
          </ol>
          <Link href="/practice?level=beginner" className="btn-primary mt-4 inline-flex">Start practising <span className="btn-arrow">→</span></Link>
        </div>
      )}
      {data && (
        <>
          <div className="grid grid-cols-2 border-l border-t border-ink-700 sm:grid-cols-3" data-testid="progress-stats">
            <Stat label="Solved" value={data.questions_solved ?? 0} note={`of ${data.questions_answered ?? 0} questions tried`} i={0} />
            <Stat label="Accuracy" value={Math.round((data.accuracy ?? 0) * 100)} suffix="%" note={`${data.correct_answers ?? 0} of ${data.total_responses} answers right`} i={1} />
            <Stat label="Avg score" value={Math.round((data.average_score ?? 0) * 100)} note="out of 100, hints included" i={2} />
            <StreakStat current={data.current_streak ?? 0} best={data.best_streak ?? 0} today={!!data.daily_done_today} i={3} />
            <Stat label="Skipped" value={data.total_skips} note="skips never lower a score" i={4} />
            <Stat label="Hints used" value={data.hints_used ?? 0} i={5} />
          </div>
          <TrendChart days={data.history ?? []} improvement={data.improvement} />
          {data.fundamentals && <FundamentalsPanel s={data.fundamentals} />}
          <Recommendations />
          <MasteryChart domains={data.domains} />
          <LanguageBreakdown rows={data.languages ?? []} />
          <RecentAttempts rows={data.recent ?? []} />
        </>
      )}
    </div>
  );
}

function Stat({ label, value, suffix = "", note, i }: { label: string; value: number; suffix?: string; note?: string; i: number }) {
  return (
    <div className="rise border-b border-r border-ink-700 p-5" style={{ ["--rd" as string]: `${i * 60}ms` }}>
      <div className="label">{label}</div>
      <div className="mt-2 font-display text-4xl font-bold text-ink-50"><CountUp to={value} delay={i * 60} />{suffix}</div>
      {note && <div className="mt-1 truncate text-[12px] text-ink-500">{note}</div>}
    </div>
  );
}

function StreakStat({ current, best, today, i }: { current: number; best: number; today: boolean; i: number }) {
  return (
    <Link href="/daily" className="rise group border-b border-r border-ink-700 p-5 transition-colors hover:bg-ink-900" style={{ ["--rd" as string]: `${i * 60}ms` }} data-testid="streak-stat">
      <div className="label group-hover:text-accent">Daily streak</div>
      <div className="mt-2 font-display text-4xl font-bold text-ink-50">
        <CountUp to={current} delay={i * 60} /><span className="ml-1 text-base font-normal text-ink-400">{current === 1 ? "day" : "days"}</span>
      </div>
      <div className="mt-1 text-[12px] text-ink-500">best {best} · today {today ? <span className="text-accent">done</span> : "not yet"}</div>
    </Link>
  );
}

const VERDICT_STYLE: Record<string, [string, string]> = {
  correct: ["Correct", "border-accent text-accent"],
  partially_correct: ["Partial", "border-ink-400 text-ink-200"],
  incorrect: ["Not yet", "border-signal text-signal-soft"],
};

function when(iso: string) {
  const t = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`).getTime();
  const mins = Math.max(0, Math.round((Date.now() - t) / 60_000));
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const h = Math.round(mins / 60);
  if (h < 24) return `${h} h ago`;
  return `${Math.round(h / 24)} d ago`;
}

function RecentAttempts({ rows }: { rows: RecentAttempt[] }) {
  return (
    <section aria-labelledby="recent-h" className="card overflow-x-auto" data-testid="recent-attempts">
      <div className="flex items-baseline justify-between border-b border-ink-700 px-5 py-3">
        <h2 id="recent-h" className="label">Recent answers</h2>
        <span className="label text-ink-500">click a question to try it again</span>
      </div>
      {rows.length === 0 ? (
        <p className="px-5 py-4 text-sm text-ink-400">Your latest answers will be listed here.</p>
      ) : (
        <table className="w-full min-w-[40rem] text-left text-sm">
          <caption className="sr-only">Your most recent answers</caption>
          <thead>
            <tr className="border-b border-ink-700">
              <th className="label px-5 py-2.5 font-normal">Question</th>
              <th className="label px-3 py-2.5 font-normal">Language · skill</th>
              <th className="label px-3 py-2.5 font-normal">Result</th>
              <th className="label px-3 py-2.5 text-right font-normal">Score</th>
              <th className="label px-5 py-2.5 text-right font-normal">When</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const [label, cls] = VERDICT_STYLE[r.verdict] ?? VERDICT_STYLE.partially_correct;
              return (
                <tr key={`${r.question_id}-${i}`} className="border-b border-ink-800 last:border-0">
                  <td className="max-w-[18rem] truncate px-5 py-2.5">
                    <Link href={`/practice?language=${r.language}&question=${r.question_id}`} className="text-ink-100 hover:text-accent">{r.title}</Link>
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[12px] text-ink-400">
                    <span className="uppercase text-ink-200">{LANG_LABEL[r.language] ?? r.language}</span> · {r.domain_name}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`inline-block border px-1.5 py-0.5 font-mono text-[10.5px] uppercase tracking-wider ${cls}`}>{label}</span>
                    {r.hints_used > 0 && <span className="ml-2 font-mono text-[11px] text-ink-500">{r.hints_used} hint{r.hints_used > 1 ? "s" : ""}</span>}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-ink-50">{Math.round(r.score * 100)}</td>
                  <td className="whitespace-nowrap px-5 py-2.5 text-right font-mono text-[12px] text-ink-500">{when(r.created_at)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}

const LANG_LABEL: Record<string, string> = {
  python: "Python", javascript: "JavaScript", php: "PHP", cpp: "C++", java: "Java", html: "HTML", css: "CSS", general: "General",
};

function LanguageBreakdown({ rows }: { rows: LanguageProgress[] }) {
  return (
    <section aria-labelledby="by-lang" className="card">
      <div className="flex items-baseline justify-between border-b border-ink-700 px-5 py-3">
        <h2 id="by-lang" className="label">Mastery by language</h2>
        <span className="label text-ink-500">answers · accuracy · avg score</span>
      </div>
      {rows.length === 0 ? (
        <p className="px-5 py-4 text-sm text-ink-400">Answer a question to see your per-language scores.</p>
      ) : (
        <ul>
          {rows.map((r) => {
            const pct = Math.round(r.average_score * 100);
            return (
              <li key={r.language} className="grid grid-cols-[6.5rem_1fr_auto] items-center gap-4 border-b border-ink-800 px-5 py-3 last:border-0" data-lang-row={r.language}>
                <span className="font-mono text-[12px] uppercase tracking-wider text-ink-100">{LANG_LABEL[r.language] ?? r.language}</span>
                <span className="h-1.5 bg-ink-800" aria-hidden="true">
                  <span className="bar-grow block h-full bg-accent" style={{ width: `${pct}%` }} />
                </span>
                <span className="font-mono text-sm text-ink-300">
                  {r.attempts} · {Math.round((r.accuracy ?? 0) * 100)}% · <span className="text-ink-50">{pct}%</span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

function FundamentalsPanel({ s }: { s: FundamentalsStatus }) {
  const done = Math.min(s.answers, s.min_answers);
  const avg = Math.round(s.recent_average * 100);
  const need = Math.round(s.pass_average * 100);
  const state = s.cleared ? "cleared" : s.experienced ? "optional" : "in progress";
  return (
    <section aria-labelledby="fund-h" className="card grid gap-5 p-5 sm:grid-cols-[1fr_auto] sm:items-center" data-testid="fundamentals-panel">
      <div>
        <div className="flex items-baseline gap-3">
          <h2 id="fund-h" className="label">00 · Fundamentals</h2>
          <span className={`font-mono text-[11px] uppercase tracking-wider ${s.cleared ? "text-accent" : "text-ink-400"}`}>{state}</span>
        </div>
        <p className="mt-2 text-sm text-ink-300">
          {s.cleared
            ? "Basics cleared: practice now covers every skill and returns to Fundamentals if they slip."
            : s.experienced
              ? "You already practise other skills. Turn on Focus: Fundamentals on the practice page to drill the basics."
              : `Answer ${s.min_answers} Fundamentals questions averaging ${need}% or more to unlock every skill.`}
        </p>
      </div>
      <div className="flex items-center gap-4 font-mono text-sm">
        <div className="flex gap-1" role="img" aria-label={`${done} of ${s.min_answers} answers`}>
          {Array.from({ length: s.min_answers }, (_, i) => (
            <span key={i} className={`h-3 w-5 border ${i < done ? "border-accent bg-accent" : "border-ink-600"}`} />
          ))}
        </div>
        <span className="text-ink-300">
          avg <span className={avg >= need ? "text-accent" : "text-ink-50"}>{s.answers ? `${avg}%` : "—"}</span>
          <span className="text-ink-500"> / {need}%</span>
        </span>
      </div>
    </section>
  );
}
