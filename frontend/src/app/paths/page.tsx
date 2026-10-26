"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type PathsOut, type PathSummary } from "@/lib/api";
import { PageIntro } from "@/components/PageIntro";
import { Bar, ContinueCard, PathMark } from "@/components/PathParts";

export default function PathsPage() {
  const [data, setData] = useState<PathsOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.paths().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/paths";
      else setError(e instanceof Error ? e.message : "Couldn't load the paths.");
    });
  }, []);

  const pass = data ? Math.round(data.pass_mark * 100) : 75;
  return (
    <div className="space-y-8">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">00 · Paths{data && ` · ${data.paths.filter((p) => p.finished).length} of ${data.paths.length} finished`}</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Pick a route.</h1>
      </div>
      <PageIntro>
        Each path goes from beginner to advanced in short steps. Score {pass}% on a step&apos;s questions or pass its coding
        exercise to open the next one. Answers you&apos;ve already given count.
      </PageIntro>

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-40 animate-pulse" />}
      {data && (
        <>
          {data.continue && <ContinueCard data={data.continue} />}
          <ul className="grid gap-px border border-ink-700 bg-ink-700 md:grid-cols-2 xl:grid-cols-3" data-testid="path-list">
            {data.paths.map((p, i) => <PathCard key={p.slug} p={p} i={i} />)}
          </ul>
          <p className="font-mono text-[12px] text-ink-500">
            +{data.step_xp} XP for each step you finish · +{data.path_xp} XP for a whole path
          </p>
        </>
      )}
    </div>
  );
}

function PathCard({ p, i }: { p: PathSummary; i: number }) {
  const status = p.finished ? "Finished" : p.started ? `Step ${p.current_step}: ${p.current_title}` : "Not started";
  return (
    <li className="rise bg-ink-950" style={{ ["--rd" as string]: `${i * 40}ms` }} data-testid={`path-${p.slug}`}>
      <Link href={`/paths/${p.slug}`} className="group flex h-full flex-col gap-4 p-5 transition-colors hover:bg-ink-900">
        <div className="flex items-start gap-4">
          <PathMark mark={p.mark} done={p.steps_done} total={p.steps_total} dim={!p.started && !p.finished} />
          <div className="min-w-0">
            <h2 className="font-display text-xl font-semibold leading-tight text-ink-50 group-hover:text-accent">{p.name}</h2>
            <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-ink-400">
              {p.steps_total} steps{p.exercises ? ` · ${p.exercises} coding exercise${p.exercises === 1 ? "" : "s"}` : ""}
            </p>
          </div>
        </div>
        <p className="flex-1 text-sm leading-relaxed text-ink-300">{p.blurb}</p>
        <div className="space-y-2">
          <div className="flex items-baseline justify-between gap-3 font-mono text-[12px]">
            <span className={`min-w-0 truncate ${p.finished ? "text-accent" : "text-ink-300"}`}>{status}</span>
            <span className="shrink-0 text-ink-400">
              <span className="text-ink-100">{p.steps_done}</span>/{p.steps_total}
            </span>
          </div>
          <Bar value={p.progress} />
        </div>
      </Link>
    </li>
  );
}
