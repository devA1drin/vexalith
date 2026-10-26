"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type BadgeGroup, type BadgeOut, type XpOut } from "@/lib/api";
import { BadgeMark } from "@/components/BadgeMark";
import { LevelCard } from "@/components/XpBar";
import { RanksTabs } from "@/components/RanksTabs";

const GROUPS: { id: BadgeGroup; title: string }[] = [
  { id: "answers", title: "Answers" },
  { id: "streaks", title: "Daily streaks" },
  { id: "languages", title: "Languages & topics" },
  { id: "code", title: "Coding exercises" },
  { id: "paths", title: "Learning paths" },
];

const RULES: [string, string][] = [
  ["Correct answer", "10 / 20 / 30 XP for beginner / intermediate / advanced, once per question. Each hint takes 10% off."],
  ["Coding exercise passed", "30 / 50 / 80 XP, once per exercise. Each hint takes 10% off, and Solved with help takes 25% off."],
  ["Daily challenge", "15 XP a day, plus a streak bonus of 5 XP for every day in a row, up to 30."],
  ["Learning paths", "25 XP for each step you finish and 100 XP for finishing a whole path."],
];

function when(iso: string | null) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

export default function BadgesPage() {
  const [data, setData] = useState<XpOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.xp().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/badges";
      else setError(e instanceof Error ? e.message : "Couldn't load your badges.");
    });
  }, []);

  return (
    <div className="space-y-8">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">04 · Progress</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Level &amp; badges</h1>
      </div>
      <RanksTabs />
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-32 animate-pulse" />}
      {data && (
        <>
          <LevelCard info={data} week={data.xp_this_week} />
          <section aria-labelledby="badges-h" className="space-y-6" data-testid="badges">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="badges-h" className="font-display text-2xl font-semibold text-ink-50">Badges</h2>
              <p className="font-mono text-[12px] text-ink-400">
                <span className="text-accent">{data.badges_earned}</span> of {data.badges.length} earned
              </p>
            </div>
            {GROUPS.map((g) => (
              <div key={g.id}>
                <p className="label mb-3">{g.title}</p>
                <ul className="grid grid-cols-1 gap-px border border-ink-700 bg-ink-700 min-[480px]:grid-cols-2 lg:grid-cols-4">
                  {data.badges.filter((b) => b.group === g.id).map((b) => <BadgeTile key={b.key} b={b} />)}
                </ul>
              </div>
            ))}
          </section>
          <div className="grid gap-6 lg:grid-cols-2">
            <section className="card p-5" aria-labelledby="rules-h">
              <h2 id="rules-h" className="font-display text-lg font-semibold text-ink-50">How XP works</h2>
              <dl className="mt-3 space-y-3 text-sm">
                {RULES.map(([k, v]) => (
                  <div key={k}>
                    <dt className="font-mono text-[12px] uppercase tracking-wider text-accent">{k}</dt>
                    <dd className="mt-0.5 text-ink-300">{v}</dd>
                  </div>
                ))}
              </dl>
              <p className="mt-4 text-[13px] text-ink-400">Your answers from before XP existed count too.</p>
            </section>
            <section className="card p-5" aria-labelledby="recent-h" data-testid="recent-xp">
              <h2 id="recent-h" className="font-display text-lg font-semibold text-ink-50">Recent XP</h2>
              {data.recent.length === 0 ? (
                <p className="mt-3 text-sm text-ink-300">Nothing yet. Get an answer right or pass a coding exercise to start.</p>
              ) : (
                <ul className="mt-3 divide-y divide-ink-800">
                  {data.recent.map((r, i) => (
                    <li key={i} className="flex items-baseline justify-between gap-3 py-2 text-sm">
                      <span className="min-w-0 truncate text-ink-200">{r.label}</span>
                      <span className="shrink-0 font-mono text-[12px] text-accent">+{r.amount}</span>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}

function BadgeTile({ b }: { b: BadgeOut }) {
  return (
    <li className={`flex items-center gap-3 p-4 ${b.earned ? "bg-ink-900" : "bg-ink-950"}`} data-testid={`badge-${b.key}`} data-earned={b.earned}>
      <BadgeMark id={b.key} group={b.group} earned={b.earned} size={52} />
      <div className="min-w-0">
        <p className={`font-display text-[15px] font-semibold ${b.earned ? "text-ink-50" : "text-ink-300"}`}>{b.name}</p>
        <p className="mt-0.5 text-[13px] leading-snug text-ink-400">{b.description}</p>
        <p className={`mt-1 font-mono text-[11px] uppercase tracking-wider ${b.earned ? "text-accent" : "text-ink-500"}`}>
          {b.earned ? `Earned ${when(b.earned_at)}` : "Locked"}
        </p>
      </div>
    </li>
  );
}
