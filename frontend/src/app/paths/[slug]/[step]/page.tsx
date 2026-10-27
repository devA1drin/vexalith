"use client";

import { BookmarkButton } from "@/components/BookmarkButton";
import { questionKey } from "@/lib/bookmarkStore";
import { ANSWER_PLACEHOLDER } from "@/lib/prefs";
import { useAnswerLanguage } from "@/lib/profileStore";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api, ApiError, type FeedbackPayload, type PathDetail, type Question } from "@/lib/api";
import { CodeBlock } from "@/components/CodeBlock";
import { FeedbackCard } from "@/components/FeedbackCard";
import { HintPanel } from "@/components/HintPanel";
import { HowToAnswer } from "@/components/HowToAnswer";
import { PromptText } from "@/components/PromptText";
import { ExerciseRow, PathMark, StepMeter } from "@/components/PathParts";
import { announceXp } from "@/lib/xp";

const LEVEL: Record<string, number> = { beginner: 1, intermediate: 2, advanced: 3 };

export default function StepPage() {
  const answerLang = useAnswerLanguage();
  const params = useParams<{ slug: string; step: string }>();
  const slug = params.slug;
  const number = Number(params.step);
  const [path, setPath] = useState<PathDetail | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [busy, setBusy] = useState<null | "load" | "submit" | "skip">(null);
  const [error, setError] = useState<string | null>(null);
  const [finished, setFinished] = useState<null | { path: boolean }>(null);
  const [count, setCount] = useState(0);
  const recent = useRef<number[]>([]);
  const started = useRef(false);

  const fail = useCallback(
    (e: unknown, fallback: string) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = `/login?callbackUrl=/paths/${slug}/${number}`;
      else setError(e instanceof ApiError && e.status === 404 ? "There's no such step." : e instanceof Error ? e.message : fallback);
    },
    [slug, number],
  );

  const loadQuestion = useCallback(async () => {
    setBusy("load");
    setError(null);
    try {
      const q = await api.pathQuestion(slug, number, recent.current);
      recent.current = [q.id, ...recent.current.filter((id) => id !== q.id)].slice(0, 6);
      setQuestion(q);
      setAnswer("");
      setFeedback(null);
      setCount((c) => c + 1);
    } catch (e) {
      fail(e, "Couldn't load a question.");
    } finally {
      setBusy(null);
    }
  }, [slug, number, fail]);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    api.path(slug).then((p) => {
      setPath(p);
      const s = p.steps[number - 1];
      if (s && s.status !== "locked") void loadQuestion();
    }).catch((e) => fail(e, "Couldn't load this step."));
  }, [slug, number, loadQuestion, fail]);

  async function onSubmit() {
    if (!question || !path) return;
    setBusy("submit");
    setError(null);
    const before = path.steps[number - 1];
    try {
      const res = await api.submitResponse(question.id, answer);
      setFeedback(res.feedback);
      void announceXp();
      const after = await api.path(slug);
      setPath(after);
      if (before.status !== "done" && after.steps[number - 1].status === "done") setFinished({ path: !path.finished && after.finished });
    } catch (e) {
      fail(e, "Submit failed");
    } finally {
      setBusy(null);
    }
  }

  async function onSkipAhead() {
    setBusy("skip");
    try {
      setPath(await api.skipAhead(slug, number));
      await loadQuestion();
    } catch (e) {
      fail(e, "Couldn't open this step.");
      setBusy(null);
    }
  }

  const step = path?.steps[number - 1];
  const next = path?.steps[number];
  const prev = path?.steps[number - 2];
  const level = question ? LEVEL[question.difficulty] ?? 1 : 0;
  const isBlank = question?.kind === "fill_blank";
  const minChars = isBlank ? 1 : 10;

  return (
    <div className="space-y-6">
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!path && !error && <div className="card h-40 animate-pulse" />}
      {path && step && (
        <>
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
            <div className="flex min-w-0 items-center gap-4">
              <PathMark mark={path.mark} done={path.steps_done} total={path.steps_total} size={52} />
              <div className="min-w-0">
                <p className="label mb-1.5">
                  <Link href={`/paths/${path.slug}`} className="hover:text-ink-50">{path.name}</Link> · step {step.number} of {path.steps_total}
                </p>
                <h1 className="font-display text-3xl font-bold tracking-tight text-ink-50 sm:text-4xl">{step.title}</h1>
              </div>
            </div>
            <Link href={`/paths/${path.slug}`} className="btn-ghost">Path map</Link>
          </div>

          {step.status === "locked" ? (
            <section className="card max-w-2xl p-5" data-testid="step-locked">
              <p className="label mb-2">Locked</p>
              <p className="text-ink-100">
                This step opens after step {prev?.number}, {prev?.title}: {Math.round(path.pass_mark * 100)}% on its questions
                {prev?.exercise ? " or its exercise passed" : ""}.
              </p>
              <p className="mt-1 text-sm text-ink-400">You can skip ahead now. Earlier steps stay open, and everything you answer here still counts.</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <button type="button" onClick={onSkipAhead} disabled={busy !== null} className="btn-primary" data-testid="skip-ahead">
                  {busy === "skip" ? "Opening…" : <>Skip ahead to this step <span className="btn-arrow">↷</span></>}
                </button>
                {prev && <Link href={`/paths/${path.slug}/${prev.number}`} className="btn-ghost">Go to step {prev.number}</Link>}
              </div>
            </section>
          ) : (
            <>
              {finished && (
                <section className="rise card relative overflow-hidden border-accent p-5 sm:p-6" data-testid="step-complete" aria-live="polite">
                  <div className="flex flex-wrap items-center gap-5">
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center bg-accent text-ink-950">
                      <svg viewBox="0 0 32 32" width="30" height="30" aria-hidden><path d="M7 17L13 23L25 9" fill="none" stroke="currentColor" strokeWidth="3.5" /></svg>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="label mb-1 text-accent">Step {step.number} done · +{path.step_xp} XP</p>
                      <p className="font-display text-2xl font-semibold text-ink-50">
                        {finished.path ? `You finished the ${path.name} path.` : `${step.title} is finished.`}
                      </p>
                      {finished.path && <p className="mt-1 text-sm text-ink-300">+{path.path_xp} XP path bonus on top.</p>}
                    </div>
                    {next && !finished.path ? (
                      <Link href={`/paths/${path.slug}/${next.number}`} className="btn-primary" data-testid="next-step">
                        Next: {next.title} <span className="btn-arrow">→</span>
                      </Link>
                    ) : (
                      <Link href={`/paths/${path.slug}`} className="btn-primary">See the path <span className="btn-arrow">→</span></Link>
                    )}
                  </div>
                </section>
              )}

              <section className="card grid gap-4 p-4 sm:p-5 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:gap-8" data-testid="step-progress">
                <div className="min-w-0 space-y-3">
                  <p className="text-sm text-ink-300">{step.blurb}</p>
                  <StepMeter step={step} passMark={path.pass_mark} />
                </div>
                <div className="min-w-0 space-y-3">
                  {step.exercise ? <ExerciseRow exercise={step.exercise} /> : <p className="font-mono text-[12px] text-ink-500">No coding exercise in this step.</p>}
                  <StepNote path={path} n={number} />
                </div>
              </section>

              {step.skipped && (
                <p className="border-l-2 border-ink-400 pl-3 text-[13px] text-ink-300" data-testid="skipped-note">
                  You skipped ahead to this step. Step {number - 1}{prev ? `, ${prev.title},` : ""} isn&apos;t finished yet, and stays open.
                </p>
              )}

              {!question && busy === "load" && <div className="card h-72 animate-pulse" />}
              {question && (
                <article key={`${question.id}-${count}`} className="card q-enter" data-question-id={question.id} data-domain={question.domain_slug}>
                  <div className="flex flex-wrap items-center gap-2 border-b border-ink-700 px-4 py-3 sm:px-6">
                    <span className="chip text-ink-100">{question.domain_name}</span>
                    <span className="chip gap-1.5" title={question.difficulty}>
                      {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
                      <span className="ml-1">{question.difficulty}</span>
                    </span>
                    {question.language !== "general" && <span className="chip">{question.language === "cpp" ? "C++" : question.language}</span>}
                    {isBlank && <span className="chip border-accent text-accent">Missing code</span>}
                    <span className="label ml-auto">#{String(question.id).padStart(3, "0")}</span>
                    <BookmarkButton itemKey={questionKey(question.id)} />
                  </div>
                  <div className="grid gap-6 p-4 sm:p-6 lg:grid-cols-2">
                    <div className="min-w-0 space-y-4">
                      <h2 className="font-display text-2xl font-semibold leading-tight text-ink-50" data-testid="question-title">{question.title}</h2>
                      <CodeBlock code={question.code} language={question.language} />
                    </div>
                    <div className="flex min-w-0 flex-col gap-4">
                      <PromptText prompt={question.prompt} />
                      <HowToAnswer question={question} />
                      <HintPanel questionId={question.id} hintCount={question.hint_count ?? 0} locked={!!feedback} />
                      <label className="flex flex-1 flex-col gap-2">
                        <span className="flex flex-wrap items-baseline justify-between gap-2">
                          <span className="label">{isBlank ? "The missing code (+ why, optional)" : "Your answer, in your own words"}</span>
                          <span className="font-mono text-[11px] text-ink-500" lang="fil">English · Filipino · Taglish</span>
                        </span>
                        <textarea
                          value={answer}
                          onChange={(e) => setAnswer(e.target.value)}
                          rows={7}
                          disabled={!!feedback || busy === "submit"}
                          placeholder={isBlank ? "e.g. i += 1" : ANSWER_PLACEHOLDER[answerLang].long}
                          className="input min-h-[10rem] flex-1 font-mono text-[13px] leading-6"
                        />
                      </label>
                      <div className="flex flex-wrap items-center gap-3">
                        {!feedback ? (
                          <>
                            <button type="button" onClick={onSubmit} disabled={answer.trim().length < minChars || busy !== null} className="btn-primary" data-testid="submit">
                              {busy === "submit" ? "Evaluating…" : <>Submit <span className="btn-arrow">→</span></>}
                            </button>
                            <button type="button" onClick={loadQuestion} disabled={busy !== null} className="btn-ghost" data-testid="another">
                              Another question
                            </button>
                          </>
                        ) : (
                          <button type="button" onClick={loadQuestion} disabled={busy !== null} className="btn-primary" data-testid="next">
                            {busy === "load" ? "Loading…" : <>Next question <span className="btn-arrow">→</span></>}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </article>
              )}
              {feedback && <FeedbackCard feedback={feedback} />}
            </>
          )}
        </>
      )}
    </div>
  );
}

/** One line on what's left in this step, only when it isn't obvious from the meter. */
function StepNote({ path, n }: { path: PathDetail; n: number }) {
  const s = path.steps[n - 1];
  const next = path.steps[n];
  if (s.status === "done") return <p className="text-[13px] text-accent">Step done. Extra answers still help your mastery.</p>;
  if (s.questions_passed && s.exercise && !s.exercise.passed)
    return <p className="text-[13px] text-ink-200">Questions done. Pass the exercise to finish the step.</p>;
  if (!s.questions_passed && s.exercise?.passed && next)
    return <p className="text-[13px] text-ink-200">Exercise passed, so step {next.number} is open. Reach {Math.round(path.pass_mark * 100)}% here to finish this step.</p>;
  return null;
}
