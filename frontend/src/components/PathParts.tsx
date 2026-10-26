"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type ContinueCard as ContinueData, type PathExercise, type PathStep } from "@/lib/api";

const LIME = "#c8f031";
const GRAPHITE = "#4a4a46";

/** A path's emblem: a notched tile with the path's short code and one tick per step (lit when done). */
export function PathMark({ mark, done, total, size = 56, dim = false }: { mark: string; done: number; total: number; size?: number; dim?: boolean }) {
  const color = dim ? GRAPHITE : LIME;
  const gap = 2;
  const width = (44 - gap * (total - 1)) / total;
  const font = mark.length >= 3 ? 15 : mark.length === 2 ? 19 : 22;
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} aria-hidden className="shrink-0">
      <path d="M4 4H46L60 18V60H4Z" fill={dim ? "#121312" : "rgba(200,240,49,0.07)"} stroke={color} strokeWidth={2} />
      <path d="M46 4V18H60" fill="none" stroke={color} strokeOpacity={0.45} strokeWidth={1} />
      <text x="30" y="30" textAnchor="middle" dominantBaseline="middle" fill={color} fontFamily="var(--font-mono), ui-monospace, monospace" fontWeight={700} fontSize={font}>
        {mark}
      </text>
      {Array.from({ length: total }, (_, i) => (
        <rect key={i} x={10 + i * (width + gap)} y={47} width={width} height={5} fill={i < done ? color : "none"} stroke={color} strokeOpacity={i < done ? 1 : 0.45} strokeWidth={1} />
      ))}
    </svg>
  );
}

/** Thin progress bar. */
export function Bar({ value, className = "" }: { value: number; className?: string }) {
  return (
    <div className={`h-1.5 bg-ink-800 ${className}`} role="presentation">
      <div className="bar-grow h-full bg-accent" style={{ width: `${Math.round(Math.min(1, Math.max(0, value)) * 100)}%` }} />
    </div>
  );
}

/** A step's question score against the pass mark. */
export function StepMeter({ step, passMark }: { step: PathStep; passMark: number }) {
  const pct = Math.round(step.score * 100);
  const need = Math.round(passMark * 100);
  return (
    <div className="space-y-2" data-testid="step-meter">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 font-mono text-[12px]">
        <span className="text-ink-300">
          Questions <span className="text-ink-50">{step.answered}/{step.target}</span>
        </span>
        <span className={step.questions_passed ? "text-accent" : "text-ink-300"}>
          {pct}% <span className="text-ink-500">· needs {need}%</span>
        </span>
      </div>
      <div className="relative h-2 bg-ink-800">
        <div className="bar-grow h-full bg-accent" style={{ width: `${Math.min(100, pct)}%` }} />
        <span className="absolute -top-1 bottom-[-4px] w-px bg-ink-100" style={{ left: `${need}%` }} aria-hidden />
      </div>
    </div>
  );
}

/** The step's coding exercise, with a link per language when any language counts. */
export function ExerciseRow({ exercise, compact = false }: { exercise: PathExercise; compact?: boolean }) {
  const passedName = exercise.options.find((o) => o.slug === exercise.passed_slug)?.language_name;
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-2" data-testid="step-exercise">
      <span className="flex items-center gap-2 font-mono text-[12px] text-ink-300">
        <span aria-hidden className={`inline-block h-2.5 w-2.5 border ${exercise.passed ? "border-accent bg-accent" : "border-ink-500"}`} />
        Exercise <span className="text-ink-50">{exercise.title}</span>
      </span>
      {exercise.passed ? (
        <span className="chip border-accent text-accent">Passed{passedName && exercise.any_language ? ` in ${passedName}` : ""}</span>
      ) : compact ? (
        <span className="font-mono text-[11px] text-ink-500">{exercise.any_language ? "any language" : exercise.options[0].language_name}</span>
      ) : (
        <span className="flex flex-wrap gap-1.5">
          {exercise.options.map((o) => (
            <Link key={o.slug} href={`/code/${o.slug}`} className="chip hover:border-accent hover:text-accent">
              {o.language_name} →
            </Link>
          ))}
        </span>
      )}
    </div>
  );
}

/** "Continue where you left off": the step to pick up next, or a first path to try. */
export function ContinueCard({ data }: { data?: ContinueData | null }) {
  const [state, setState] = useState<ContinueData | null | undefined>(data);
  const [hidden, setHidden] = useState(false);
  useEffect(() => {
    if (data !== undefined) {
      setState(data);
      return;
    }
    api.paths().then((p) => setState(p.continue)).catch(() => setHidden(true));
  }, [data]);
  if (hidden || state === undefined) return null;
  if (state === null) {
    return (
      <section className="card flex flex-wrap items-center gap-4 p-5" data-testid="continue-card" aria-label="Learning paths">
        <PathMark mark="01" done={0} total={4} size={52} />
        <div className="min-w-0 flex-1">
          <p className="label mb-1">Learning paths</p>
          <p className="font-display text-lg font-semibold text-ink-50">Not sure where to start? Follow a path.</p>
          <p className="text-sm text-ink-300">Short steps from beginner to advanced, with a coding exercise along the way.</p>
        </div>
        <Link href="/paths" className="btn-ghost">See paths <span className="btn-arrow">→</span></Link>
      </section>
    );
  }
  const { path, step } = state;
  return (
    <section className="card relative overflow-hidden border-accent/60 p-5" data-testid="continue-card" aria-label="Continue where you left off">
      <div className="flex flex-wrap items-center gap-4">
        <PathMark mark={path.mark} done={path.steps_done} total={path.steps_total} size={56} />
        <div className="min-w-0 flex-1">
          <p className="label mb-1 text-accent">Continue where you left off</p>
          <p className="font-display text-xl font-semibold leading-tight text-ink-50">
            {path.name} <span className="text-ink-500">/</span> {step.title}
          </p>
          <p className="mt-1 font-mono text-[12px] text-ink-400">
            Step {step.number} of {path.steps_total} · {path.steps_done} done{state.from_history ? " · counted from your past answers" : ""}
          </p>
        </div>
        <Link href={`/paths/${path.slug}/${step.number}`} className="btn-primary" data-testid="continue-link">
          Continue <span className="btn-arrow">→</span>
        </Link>
      </div>
      <Bar value={path.progress} className="mt-4" />
    </section>
  );
}
