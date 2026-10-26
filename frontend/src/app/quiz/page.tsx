"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError, type QuizHistory, type QuizOptions, type QuizScope } from "@/lib/api";
import { PageIntro } from "@/components/PageIntro";
import { PracticeTabs } from "@/components/PracticeTabs";
import { ago, mmss } from "@/lib/when";

const SCOPES: { id: QuizScope; label: string }[] = [
  { id: "language", label: "Language" },
  { id: "topic", label: "Topic" },
  { id: "path", label: "Path" },
  { id: "mixed", label: "Mixed" },
];
const SCOPE_WORD: Record<QuizScope, string> = { language: "Language", topic: "Topic", path: "Path", mixed: "Mixed" };

export default function QuizSetupPage() {
  const router = useRouter();
  const [opts, setOpts] = useState<QuizOptions | null>(null);
  const [hist, setHist] = useState<QuizHistory | null>(null);
  const [scope, setScope] = useState<QuizScope>("language");
  const [value, setValue] = useState("");
  const [length, setLength] = useState(10);
  const [minutes, setMinutes] = useState(10);
  const [instant, setInstant] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    Promise.all([api.quizOptions(), api.quizHistory()]).then(([o, h]) => {
      setOpts(o);
      setHist(h);
      const s = (q.get("scope") as QuizScope) || "language";
      const sc = o.scopes[s] ? s : "language";
      const want = q.get("value") ?? (sc === "language" ? localStorage.getItem("vexalith_language") : null);
      const list = o.scopes[sc];
      setScope(sc);
      setValue(list.find((x) => x.value === want)?.value ?? list[0]?.value ?? "");
      const len = Number(q.get("length"));
      const min = Number(q.get("minutes"));
      if (o.lengths.includes(len)) setLength(len);
      if (o.minutes.includes(min)) setMinutes(min);
      if (q.get("instant") === "1") setInstant(true);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/quiz";
      else setError(e instanceof Error ? e.message : "Couldn't load the quiz options.");
    });
  }, []);

  const pickScope = (s: QuizScope) => {
    setScope(s);
    setValue(opts?.scopes[s][0]?.value ?? "");
  };

  const start = async () => {
    setBusy(true);
    setError(null);
    try {
      const q = await api.startQuiz({ scope, value, length, minutes, instant });
      router.push(`/quiz/${q.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't start the quiz.");
      setBusy(false);
    }
  };

  const endActive = async () => {
    if (!opts?.active) return;
    setBusy(true);
    try {
      const r = await api.finishQuiz(opts.active.id);
      router.push(`/quiz/${r.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't end that quiz.");
      setBusy(false);
    }
  };

  const list = opts?.scopes[scope] ?? [];
  const pool = list.find((x) => x.value === value)?.count ?? 0;
  const rules = opts?.rules;
  return (
    <div className="space-y-8">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">01 · Practice · Timed quiz</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Beat the clock.</h1>
      </div>
      <PracticeTabs />
      <PageIntro>
        A short run of quick questions against a timer. Answer in English, Filipino or Taglish. The clock keeps going if you leave
        or refresh, and whatever you&apos;ve typed is sent when time runs out.
      </PageIntro>

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!opts && !error && <div className="card h-72 animate-pulse" />}

      {opts?.active && (
        <div className="flex flex-wrap items-center gap-3 border border-accent bg-accent/10 px-4 py-3" data-testid="active-quiz">
          <span className="h-2 w-2 animate-pulse bg-accent" aria-hidden="true" />
          <span className="text-[14px] text-ink-100">
            A quiz is running: <b>{opts.active.scope_label}</b> · {opts.active.length} questions · {mmss(opts.active.remaining_s)} left
          </span>
          <div className="ml-auto flex gap-2">
            <Link href={`/quiz/${opts.active.id}`} className="btn-primary py-[7px]">Resume <span className="btn-arrow">→</span></Link>
            <button type="button" className="btn-ghost py-[7px]" onClick={endActive} disabled={busy}>End it</button>
          </div>
        </div>
      )}

      {opts && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <section className="card divide-y divide-ink-800" data-testid="quiz-setup">
            <Step n="01" title="What to practise">
              <Segment
                label="Scope"
                value={scope}
                options={SCOPES.filter((s) => opts.scopes[s.id].length).map((s) => ({ value: s.id, label: s.label }))}
                onChange={(v) => pickScope(v as QuizScope)}
                cols={4}
              />
              {scope !== "mixed" && (
                <select value={value} onChange={(e) => setValue(e.target.value)} className="input mt-3 w-full" data-testid="quiz-value" aria-label={SCOPE_WORD[scope]}>
                  {list.map((o) => (
                    <option key={o.value} value={o.value}>{o.label} ({o.count} questions)</option>
                  ))}
                </select>
              )}
              {scope === "mixed" && <p className="mt-3 text-[13px] text-ink-400">A bit of every language and topic.</p>}
            </Step>
            <Step n="02" title="How many questions">
              <Segment label="Questions" value={String(length)} options={opts.lengths.map((n) => ({ value: String(n), label: String(n), off: n > pool && scope !== "mixed" }))} onChange={(v) => setLength(Number(v))} cols={3} />
              {length > pool && scope !== "mixed" && <p className="mt-2 font-mono text-[11px] text-ink-500">Only {pool} here, so you&apos;ll get {pool}.</p>}
            </Step>
            <Step n="03" title="Time limit">
              <Segment label="Minutes" value={String(minutes)} options={opts.minutes.map((n) => ({ value: String(n), label: `${n} min` }))} onChange={(v) => setMinutes(Number(v))} cols={3} />
            </Step>
            <Step n="04" title="Feedback">
              <Segment
                label="Feedback"
                value={instant ? "1" : "0"}
                options={[{ value: "0", label: "At the end" }, { value: "1", label: "After each one" }]}
                onChange={(v) => setInstant(v === "1")}
                cols={2}
              />
              <p className="mt-2 text-[13px] text-ink-400">
                {instant ? "See if you were right straight away. Reading feedback uses your time." : "No interruptions. You see every answer when you finish."}
              </p>
            </Step>
            <div className="flex flex-wrap items-center gap-4 p-4 sm:p-5">
              <button type="button" className="btn-primary" onClick={start} disabled={busy || !!opts.active || (scope !== "mixed" && !value)} data-testid="start-quiz">
                {busy ? "Starting…" : <>Start · {Math.min(length, scope === "mixed" ? length : pool || length)} questions · {minutes}:00 <span className="btn-arrow">→</span></>}
              </button>
              {opts.active && <span className="font-mono text-[11px] text-ink-500">Finish the running quiz first.</span>}
            </div>
          </section>

          <aside className="space-y-6">
            {rules && (
              <div className="panel space-y-2 p-4 text-[13px] leading-relaxed text-ink-300" data-testid="quiz-rules">
                <div className="label">How it counts</div>
                <p>+{rules.quiz_xp} XP extra for each question you get right for the first time in a quiz, on top of the usual answer XP. Questions you&apos;ve already got right earn nothing again.</p>
                <p>Score {Math.round(rules.beat_score * 100)}% or more on a quiz of {rules.beat_min}+ questions to earn the Beat the Clock badge.</p>
                <p>Anything you miss goes to <Link href="/review" className="text-accent underline-offset-4 hover:underline">Review mistakes</Link>.</p>
              </div>
            )}
            {hist && <BestScores hist={hist} />}
          </aside>
        </div>
      )}

      {hist && <History hist={hist} />}
    </div>
  );
}

function Step({ n, title, children }: { n: string; title: string; children: React.ReactNode }) {
  return (
    <div className="p-4 sm:p-5">
      <div className="mb-3 flex items-baseline gap-3">
        <span className="font-mono text-[12px] text-accent">{n}</span>
        <h2 className="font-display text-lg font-semibold text-ink-50">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function Segment({ label, value, options, onChange, cols }: { label: string; value: string; options: { value: string; label: string; off?: boolean }[]; onChange: (v: string) => void; cols: number }) {
  const grid = { 2: "grid-cols-2", 3: "grid-cols-3", 4: "grid-cols-2 sm:grid-cols-4" }[cols] ?? "grid-cols-3";
  return (
    <div role="radiogroup" aria-label={label} className={`grid ${grid} gap-px border border-ink-700 bg-ink-700`}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={value === o.value}
          onClick={() => onChange(o.value)}
          className={`px-3 py-2.5 font-mono text-[13px] uppercase tracking-wider transition-colors ${
            value === o.value ? "bg-accent text-ink-950" : `bg-ink-950 hover:text-ink-50 ${o.off ? "text-ink-600" : "text-ink-300"}`
          }`}
          data-testid={`seg-${label.toLowerCase()}-${o.value || "all"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function pct(s: number) {
  return `${Math.round(s * 100)}%`;
}

function BestScores({ hist }: { hist: QuizHistory }) {
  if (!hist.best.length) return null;
  return (
    <section className="space-y-2" data-testid="best-scores">
      <h2 className="label">Best scores</h2>
      <ul className="divide-y divide-ink-800 border border-ink-700">
        {hist.best.slice(0, 6).map((b) => (
          <li key={`${b.scope}:${b.scope_value}`} className="flex items-center gap-3 px-4 py-2.5">
            <div className="min-w-0 flex-1">
              <div className="truncate text-[14px] text-ink-100">{b.scope_label}</div>
              <div className="font-mono text-[11px] text-ink-500">{SCOPE_WORD[b.scope]} · {b.attempts} {b.attempts === 1 ? "try" : "tries"}</div>
            </div>
            <div className="text-right">
              <div className={`font-display text-xl font-bold tabular-nums ${b.best_score >= 0.8 ? "text-accent" : "text-ink-50"}`}>{pct(b.best_score)}</div>
              <div className="font-mono text-[11px] text-ink-500">{b.best_correct}/{b.best_length}</div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

const ENDED: Record<string, string> = { done: "Finished", time: "Time ran out", ended: "Ended early" };

function History({ hist }: { hist: QuizHistory }) {
  return (
    <section className="space-y-3" data-testid="quiz-history">
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="font-display text-2xl font-semibold text-ink-50">Your quizzes</h2>
        <span className="font-mono text-[12px] text-ink-500">{hist.total} taken</span>
      </div>
      {hist.quizzes.length === 0 ? (
        <p className="text-[14px] text-ink-400">No quizzes yet. Your results show up here.</p>
      ) : (
        <ul className="divide-y divide-ink-800 border border-ink-700">
          {hist.quizzes.map((q) => (
            <li key={q.id}>
              <Link href={`/quiz/${q.id}`} className="grid grid-cols-[3.5rem_minmax(0,1fr)_auto] items-center gap-3 px-4 py-3 transition-colors hover:bg-ink-900 sm:grid-cols-[4rem_minmax(0,1fr)_8rem_8rem_auto]">
                <span className={`font-display text-xl font-bold tabular-nums ${q.score >= 0.8 ? "text-accent" : "text-ink-50"}`}>{pct(q.score)}</span>
                <span className="min-w-0">
                  <span className="block truncate text-[14px] text-ink-100">{q.scope_label}</span>
                  <span className="block font-mono text-[11px] text-ink-500">{q.correct}/{q.length} right · {ago(q.finished_at)}</span>
                </span>
                <span className="hidden font-mono text-[12px] text-ink-400 sm:block">{mmss(q.time_used_s)} / {mmss(q.time_limit_s)}</span>
                <span className={`hidden font-mono text-[12px] sm:block ${q.ended_by === "time" ? "text-signal-soft" : "text-ink-400"}`}>{ENDED[q.ended_by] ?? q.ended_by}</span>
                <span className="text-ink-500" aria-hidden="true">→</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
