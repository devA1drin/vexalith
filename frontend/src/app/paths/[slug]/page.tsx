"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError, type PathDetail, type PathStep } from "@/lib/api";
import { Bar, ExerciseRow, PathMark, StepMeter } from "@/components/PathParts";

export default function PathPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const [data, setData] = useState<PathDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.path(slug).then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = `/login?callbackUrl=/paths/${slug}`;
      else setError(e instanceof ApiError && e.status === 404 ? "There's no path with that name." : e instanceof Error ? e.message : "Couldn't load this path.");
    });
  }, [slug]);

  async function skipTo(n: number) {
    setBusy(true);
    try {
      await api.skipAhead(slug, n);
      router.push(`/paths/${slug}/${n}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't open that step.");
      setBusy(false);
    }
  }

  const current = data?.steps.find((s) => s.number === data.current_step);
  return (
    <div className="space-y-8">
      <Link href="/paths" className="font-mono text-[12px] uppercase tracking-wider text-ink-400 hover:text-ink-50">← All paths</Link>
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-48 animate-pulse" />}
      {data && (
        <>
          <header className="flex flex-wrap items-start gap-5 border-b border-ink-700 pb-6">
            <PathMark mark={data.mark} done={data.steps_done} total={data.steps_total} size={76} />
            <div className="min-w-0 flex-1 basis-64">
              <p className="label mb-2">00 · Paths · {data.steps_done} of {data.steps_total} steps done</p>
              <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">{data.name}</h1>
              <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-ink-300">{data.blurb}</p>
              <Bar value={data.progress} className="mt-4 max-w-md" />
            </div>
            {!data.finished && current && (
              <Link href={`/paths/${data.slug}/${current.number}`} className="btn-primary" data-testid="path-continue">
                {data.started ? "Continue" : "Start"} step {current.number} <span className="btn-arrow">→</span>
              </Link>
            )}
          </header>
          {data.finished && (
            <p className="card border-accent p-4 text-sm text-ink-100" data-testid="path-finished">
              <span className="font-mono text-[12px] uppercase tracking-wider text-accent">Path finished · +{data.path_xp} XP </span>
              Every step is done. You can still practise any of them.
            </p>
          )}
          <ol className="relative space-y-3" data-testid="steps">
            <span aria-hidden className="absolute bottom-6 left-[15px] top-6 w-px bg-ink-700" />
            {data.steps.map((s) => (
              <StepRow
                key={s.key}
                s={s}
                slug={data.slug}
                passMark={data.pass_mark}
                current={s.number === data.current_step && !data.finished}
                prev={data.steps[s.number - 2]}
                confirming={confirm === s.number}
                busy={busy}
                onAsk={() => setConfirm(s.number)}
                onCancel={() => setConfirm(null)}
                onSkip={() => skipTo(s.number)}
              />
            ))}
          </ol>
        </>
      )}
    </div>
  );
}

function Node({ s }: { s: PathStep }) {
  const base = "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center font-mono text-[12px] font-bold";
  if (s.status === "done")
    return (
      <span className={`${base} bg-accent text-ink-950`} aria-label="Done">
        <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden><path d="M3 8.5L6.5 12L13 4.5" fill="none" stroke="currentColor" strokeWidth="2.2" /></svg>
      </span>
    );
  if (s.status === "open") return <span className={`${base} border-2 border-accent bg-ink-950 text-accent`}>{s.number}</span>;
  return (
    <span className={`${base} border border-dashed border-ink-500 bg-ink-950 text-ink-500`} aria-label="Locked">
      <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden><path d="M4.5 7V5a3.5 3.5 0 0 1 7 0v2M3.5 7h9v6.5h-9z" fill="none" stroke="currentColor" strokeWidth="1.5" /></svg>
    </span>
  );
}

function StepRow({ s, slug, passMark, current, prev, confirming, busy, onAsk, onCancel, onSkip }: {
  s: PathStep; slug: string; passMark: number; current: boolean; prev?: PathStep;
  confirming: boolean; busy: boolean; onAsk: () => void; onCancel: () => void; onSkip: () => void;
}) {
  const locked = s.status === "locked";
  return (
    <li className="flex gap-4" data-testid={`step-${s.number}`} data-status={s.status}>
      <Node s={s} />
      <div className={`min-w-0 flex-1 border p-4 sm:p-5 ${current ? "border-accent/70 bg-ink-900" : locked ? "border-ink-800 bg-ink-950" : "border-ink-700 bg-ink-900"}`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="label mb-1">
              Step {s.number} · {s.levels}
              {s.status === "done" && <span className="text-accent"> · done</span>}
              {current && <span className="text-accent"> · you are here</span>}
            </p>
            <h2 className={`font-display text-lg font-semibold leading-tight ${locked ? "text-ink-300" : "text-ink-50"}`}>{s.title}</h2>
            <p className={`mt-1 text-sm ${locked ? "text-ink-500" : "text-ink-300"}`}>{s.blurb}</p>
          </div>
          {!locked && (
            <Link href={`/paths/${slug}/${s.number}`} className={s.status === "done" ? "btn-ghost" : "btn-primary"} data-testid={`open-${s.number}`}>
              {s.status === "done" ? "Practise again" : s.answered ? "Continue" : "Start"} <span className="btn-arrow">→</span>
            </Link>
          )}
          {locked && !confirming && (
            <button type="button" onClick={onAsk} className="btn-ghost" data-testid={`skip-${s.number}`}>
              Skip ahead <span className="btn-arrow">↷</span>
            </button>
          )}
        </div>
        {s.skipped && (
          <p className="mt-3 border-l-2 border-ink-400 pl-3 text-[13px] text-ink-300" data-testid="skipped-note">
            You skipped ahead to this step. Step {s.number - 1} isn&apos;t finished yet, and stays open.
          </p>
        )}
        {locked && confirming && prev && (
          <div className="mt-4 border border-ink-600 bg-ink-950 p-4" data-testid="skip-confirm" role="group" aria-label="Skip ahead">
            <p className="text-sm text-ink-100">
              This step opens after step {prev.number}, {prev.title}: {Math.round(passMark * 100)}% on its questions
              {prev.exercise ? " or its exercise passed" : ""}.
            </p>
            <p className="mt-1 text-[13px] text-ink-400">
              You can skip ahead now. Earlier steps stay open, and everything you answer here still counts.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button type="button" onClick={onSkip} disabled={busy} className="btn-primary" data-testid="skip-confirm-yes">
                {busy ? "Opening…" : <>Open step {s.number} <span className="btn-arrow">→</span></>}
              </button>
              <button type="button" onClick={onCancel} className="btn-ghost">Not now</button>
            </div>
          </div>
        )}
        {!locked && (
          <div className="mt-4 grid gap-3 border-t border-ink-800 pt-4 md:grid-cols-2 md:gap-6">
            <StepMeter step={s} passMark={passMark} />
            {s.exercise && <ExerciseRow exercise={s.exercise} compact />}
          </div>
        )}
        {locked && !confirming && (
          <p className="mt-3 font-mono text-[11px] text-ink-500">
            {s.target} questions{s.exercise ? ` · exercise: ${s.exercise.title}` : ""}
          </p>
        )}
      </div>
    </li>
  );
}
