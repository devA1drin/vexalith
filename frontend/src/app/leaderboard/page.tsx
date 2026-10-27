"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type LeaderboardEntry, type LeaderboardOut, type Visibility, type XpProfile } from "@/lib/api";
import Link from "next/link";
import { LevelMark } from "@/components/BadgeMark";
import { Avatar } from "@/components/Avatar";
import { refreshProfile } from "@/lib/profileStore";
import { RanksTabs } from "@/components/RanksTabs";

type Period = "week" | "all";

function weekLabel(start?: string, end?: string) {
  if (!start || !end) return "";
  // Manila weeks: show the dates as they are in Manila (UTC+8).
  const fmt = (iso: string, back = 0) =>
    new Date(new Date(iso).getTime() - back).toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "Asia/Manila" });
  return `${fmt(start)} to ${fmt(end, 1)} · resets Monday 12 AM Manila time`;
}

export default function LeaderboardPage() {
  const [period, setPeriod] = useState<Period>("week");
  const [data, setData] = useState<LeaderboardOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback((p: Period) => {
    setData(null);
    api.leaderboard(p).then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/leaderboard";
      else setError(e instanceof Error ? e.message : "Couldn't load the leaderboard.");
    });
  }, []);

  useEffect(() => load(period), [period, load]);

  return (
    <div className="space-y-8">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">04 · Progress</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Leaderboard</h1>
      </div>
      <RanksTabs />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <section aria-label="Rankings" className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="inline-flex border border-ink-700" role="tablist" aria-label="Period">
              {(["week", "all"] as Period[]).map((p) => (
                <button
                  key={p}
                  type="button"
                  role="tab"
                  aria-selected={period === p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 font-mono text-[12px] uppercase tracking-wider transition-colors ${period === p ? "bg-accent text-ink-950" : "text-ink-300 hover:text-ink-50"}`}
                  data-testid={`period-${p}`}
                >
                  {p === "week" ? "This week" : "All time"}
                </button>
              ))}
            </div>
            {data?.period === "week" && <p className="font-mono text-[11px] text-ink-400" data-testid="week-range">{weekLabel(data.week_start, data.week_end)}</p>}
          </div>
          {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
          {!data && !error && <div className="card h-72 animate-pulse" />}
          {data && <Board data={data} />}
        </section>
        <Appearance onChange={() => load(period)} />
      </div>
    </div>
  );
}

function Board({ data }: { data: LeaderboardOut }) {
  const { entries, you } = data;
  if (!entries.length) {
    return (
      <div className="card p-6 text-sm text-ink-300" data-testid="board-empty">
        {data.period === "week" ? "No one has earned XP this week yet. Your next correct answer puts you on the board." : "No one has earned XP yet."}
      </div>
    );
  }
  const showYou = you.visibility !== "hidden" && you.rank !== null && !you.in_top;
  return (
    <div className="card overflow-hidden" data-testid="board">
      <YouNote data={data} />
      <div className="grid grid-cols-[3rem_minmax(0,1fr)_auto] gap-3 border-b border-ink-700 px-4 py-2 label">
        <span>Rank</span>
        <span>Learner</span>
        <span className="text-right">XP</span>
      </div>
      <ol>
        {entries.map((e) => <Row key={`${e.rank}-${e.name}`} e={e} />)}
      </ol>
      {showYou && (
        <>
          <div className="border-t border-dashed border-ink-700 px-4 py-1 text-center font-mono text-[11px] text-ink-500">· · ·</div>
          <Row e={{ rank: you.rank as number, name: you.name, xp: you.xp, level: you.level, level_name: you.level_name, is_you: true, avatar: you.avatar }} />
        </>
      )}
    </div>
  );
}

function Row({ e }: { e: LeaderboardEntry }) {
  return (
    <li
      className={`grid grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-3 border-b border-ink-800 px-4 py-2.5 last:border-b-0 ${e.is_you ? "bg-accent/10" : ""}`}
      data-testid={e.is_you ? "board-you" : "board-row"}
    >
      <span className={`font-mono text-[15px] font-bold ${e.rank <= 3 ? "text-accent" : "text-ink-300"}`}>{e.rank}</span>
      <span className="flex min-w-0 items-center gap-2.5">
        {e.avatar ? <Avatar mark={e.avatar} name={e.name} size={28} /> : <LevelMark level={e.level} size={24} />}
        <span className="min-w-0">
          <span className={`block truncate text-[15px] ${e.is_you ? "font-semibold text-ink-50" : "text-ink-100"}`}>
            {e.name}
            {e.is_you && <span className="ml-2 font-mono text-[11px] uppercase tracking-wider text-accent">You</span>}
          </span>
          <span className="block font-mono text-[11px] text-ink-400">{e.level_name}</span>
        </span>
      </span>
      <span className="font-mono text-[14px] text-ink-50">{e.xp.toLocaleString()}</span>
    </li>
  );
}

function YouNote({ data }: { data: LeaderboardOut }) {
  const { you } = data;
  let text = "";
  if (you.visibility === "hidden") {
    text = you.rank ? `You're hidden from the leaderboard. You'd be #${you.rank} with ${you.xp.toLocaleString()} XP.` : "You're hidden from the leaderboard.";
  } else if (you.rank === null) {
    text = data.period === "week" ? "You haven't earned XP this week yet." : "Earn some XP to get on the board.";
  }
  if (!text) return null;
  return <p className="border-b border-ink-700 border-l-2 border-l-accent bg-accent/5 px-4 py-3 text-[13px] text-ink-200" data-testid="you-note">{text}</p>;
}

const OPTIONS: { v: Visibility; title: string; note: (p: XpProfile) => string }[] = [
  { v: "handle", title: "My handle", note: (p) => p.handle },
  { v: "name", title: "My name", note: (p) => p.name ?? "" },
  { v: "anonymous", title: "Anonymous learner", note: () => "No name or handle" },
  { v: "hidden", title: "Hide me", note: () => "Leave me off the leaderboard" },
];

function Appearance({ onChange }: { onChange: () => void }) {
  const [p, setP] = useState<XpProfile | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.xpProfile().then(setP).catch(() => setP(null));
  }, []);

  const save = async (fn: () => Promise<XpProfile>) => {
    setBusy(true);
    try {
      setP(await fn());
      onChange();
      refreshProfile();
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card h-fit p-5" aria-labelledby="appear-h" data-testid="appearance">
      <h2 id="appear-h" className="font-display text-lg font-semibold text-ink-50">How you appear</h2>
      <p className="mt-1 text-[13px] text-ink-400">Your email is never shown.</p>
      {!p ? (
        <div className="mt-4 h-40 animate-pulse bg-ink-800" />
      ) : (
        <fieldset className="mt-4 min-w-0 space-y-2" disabled={busy}>
          <legend className="sr-only">Show me on the leaderboard as</legend>
          {OPTIONS.filter((o) => o.v !== "name" || p.name_available).map((o) => (
            <label
              key={o.v}
              className={`flex cursor-pointer items-start gap-3 border p-3 transition-colors ${p.visibility === o.v ? "border-accent bg-accent/5" : "border-ink-700 hover:border-ink-500"}`}
              data-testid={`visibility-${o.v}`}
            >
              <input
                type="radio"
                name="visibility"
                className="mt-1 accent-[#c8f031]"
                checked={p.visibility === o.v}
                onChange={() => save(() => api.setVisibility(o.v))}
              />
              <span className="min-w-0">
                <span className="block text-sm text-ink-50">{o.title}</span>
                <span className="block break-words font-mono text-[12px] text-ink-400">{o.note(p)}</span>
              </span>
            </label>
          ))}
          <button type="button" className="btn-ghost mt-2 w-full" onClick={() => save(api.newHandle)} data-testid="new-handle">
            New random handle
          </button>
          <Link href="/profile#leaderboard" className="block pt-1 text-center font-mono text-[12px] text-ink-400 underline-offset-4 hover:text-accent hover:underline">
            Choose your own handle and mark
          </Link>
        </fieldset>
      )}
    </section>
  );
}
