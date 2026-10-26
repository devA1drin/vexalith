"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api, ApiError, type FeedbackPayload, type QuizResults, type QuizSlot, type QuizState } from "@/lib/api";
import { QuestionBody } from "@/components/QuestionBody";
import { QuizResultsView } from "@/components/QuizResultsView";
import { announceXp } from "@/lib/xp";
import { mmss } from "@/lib/when";

const URGENT_S = 60;
const draftKey = (id: number, pos: number) => `vx-quiz-${id}-${pos}`;

export default function QuizPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const [state, setState] = useState<QuizState | null>(null);
  const [results, setResults] = useState<QuizResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const showResults = useCallback(async (r?: QuizResults) => {
    const out = r ?? (await api.quizResults(id));
    setResults(out);
    announceXp();
    for (let p = 0; p < out.length; p++) sessionStorage.removeItem(draftKey(id, p));
  }, [id]);

  useEffect(() => {
    if (!Number.isFinite(id)) return;
    api.quiz(id).then((s) => {
      if (s.status === "finished") return showResults();
      setState(s);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = `/login?callbackUrl=/quiz/${id}`;
      else setError(e instanceof ApiError && e.status === 404 ? "That quiz doesn't exist." : e instanceof Error ? e.message : "Couldn't load the quiz.");
    });
  }, [id, showResults]);

  if (error)
    return (
      <div className="space-y-4">
        <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>
        <Link href="/quiz" className="btn-ghost">Back to Timed quiz</Link>
      </div>
    );
  if (results) return <QuizResultsView r={results} />;
  if (!state) return <div className="card h-72 animate-pulse" />;
  return <Runner initial={state} onDone={showResults} />;
}

function Runner({ initial, onDone }: { initial: QuizState; onDone: (r?: QuizResults) => Promise<void> }) {
  const id = initial.id;
  const [slots, setSlots] = useState<QuizSlot[]>(initial.slots);
  const [cur, setCur] = useState<number | null>(initial.current);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [busy, setBusy] = useState<"submit" | "finish" | null>(null);
  const [confirmEnd, setConfirmEnd] = useState(false);
  const [timeUp, setTimeUp] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const offset = useRef(Date.parse(initial.server_now) - Date.now());
  const deadline = Date.parse(initial.deadline_at);
  const [left, setLeft] = useState(() => (deadline - (Date.now() + offset.current)) / 1000);
  const chain = useRef<Promise<unknown>>(Promise.resolve());
  const ending = useRef(false);
  const answerRef = useRef("");
  answerRef.current = answer;
  const curRef = useRef(cur);
  curRef.current = cur;

  const question = cur !== null ? initial.questions[cur] : null;
  const returning = cur !== null && slots[cur]?.state === "skipped";

  // Restore this question's draft (kept per quiz and position, so a refresh doesn't lose it).
  useEffect(() => {
    setAnswer(cur !== null ? sessionStorage.getItem(draftKey(id, cur)) ?? "" : "");
  }, [cur, id]);

  const typing = (v: string) => {
    setAnswer(v);
    if (cur !== null) sessionStorage.setItem(draftKey(id, cur), v);
  };

  const queue = (fn: () => Promise<unknown>) => {
    const p = chain.current.then(fn).catch((e) => {
      if (!(e instanceof ApiError && e.status === 409)) setNote("One answer didn't save. It will be retried when the quiz ends.");
    });
    chain.current = p;
    return p;
  };

  const end = useCallback(async () => {
    if (ending.current) return;
    ending.current = true;
    setBusy("finish");
    const pos = curRef.current;
    const text = answerRef.current.trim();
    if (pos !== null && text) {
      // Whatever is typed when time runs out (or on Finish now) is sent as the answer.
      chain.current = chain.current.then(() => api.quizAnswer(id, pos, text)).catch(() => undefined);
    }
    await chain.current;
    try {
      const r = await api.finishQuiz(id);
      await onDone(r);
    } catch {
      await onDone();
    }
  }, [id, onDone]);

  // The countdown. The server holds the real start time; this only draws it.
  useEffect(() => {
    const tick = () => {
      const s = (deadline - (Date.now() + offset.current)) / 1000;
      setLeft(s);
      if (s <= 0 && !ending.current) {
        setTimeUp(true);
        end();
      }
    };
    tick();
    const t = window.setInterval(tick, 250);
    return () => window.clearInterval(t);
  }, [deadline, end]);

  const nextFrom = (list: QuizSlot[], from: number): number | null => {
    const n = list.length;
    for (let k = 1; k <= n; k++) {
      const p = (from + k) % n;
      if (list[p].state === "open") return p;
    }
    for (let k = 1; k <= n; k++) {
      const p = (from + k) % n;
      if (list[p].state === "skipped") return p;
    }
    return null;
  };

  const advance = (list: QuizSlot[], from: number) => {
    const nxt = nextFrom(list, from);
    setFeedback(null);
    setConfirmEnd(false);
    if (nxt === null) end();
    else setCur(nxt);
  };

  const submit = async () => {
    if (cur === null || !answer.trim()) return;
    const pos = cur;
    const text = answer.trim();
    const list = slots.map((s) => (s.position === pos ? { ...s, state: "answered" as const } : s));
    sessionStorage.removeItem(draftKey(id, pos));
    if (!initial.instant) {
      setSlots(list);
      queue(() => api.quizAnswer(id, pos, text));
      advance(list, pos);
      return;
    }
    setBusy("submit");
    try {
      await chain.current;
      const s = await api.quizAnswer(id, pos, text);
      setSlots(s.slots);
      setFeedback(s.feedback ?? null);
      if (s.status === "finished") ending.current = true;
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        ending.current = true;
        await onDone();
        return;
      }
      setNote(e instanceof Error ? e.message : "Couldn't send that answer.");
    } finally {
      setBusy(null);
    }
  };

  const afterFeedback = () => {
    if (ending.current) {
      ending.current = false;
      end();
      return;
    }
    if (cur !== null) advance(slots, cur);
  };

  const skip = () => {
    if (cur === null) return;
    const pos = cur;
    const list = slots.map((s) => (s.position === pos ? { ...s, state: "skipped" as const } : s));
    setSlots(list);
    queue(() => api.quizSkip(id, pos));
    const nxt = nextFrom(list, pos);
    if (nxt !== null && nxt !== pos) setCur(nxt);
  };

  const answered = slots.filter((s) => s.state === "answered").length;
  const others = slots.filter((s) => s.state !== "answered" && s.position !== cur).length;
  const urgent = left <= URGENT_S;
  const frac = Math.max(0, Math.min(1, left / initial.time_limit_s));
  return (
    <div className="space-y-5">
      <TimerBar
        label={initial.scope_label}
        n={(cur ?? 0) + 1}
        total={initial.length}
        answered={answered}
        left={left}
        frac={frac}
        urgent={urgent}
        slots={slots}
        cur={cur}
        instant={initial.instant}
      />
      {urgent && !timeUp && (
        <p role="status" className="border-l-2 border-signal bg-signal/10 px-3 py-2 text-[14px] text-signal-soft" data-testid="almost-up">
          Under a minute left. Whatever you&apos;ve typed is sent when the time runs out.
        </p>
      )}
      {note && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{note}</p>}

      {(timeUp || busy === "finish") && (
        <div className="card flex flex-col items-center gap-3 p-10 text-center" data-testid="time-up">
          <span className={`font-display text-4xl font-bold ${timeUp ? "text-signal" : "text-ink-50"}`}>{timeUp ? "Time's up." : "Finishing…"}</span>
          <span className="font-mono text-[12px] text-ink-400">Checking your answers…</span>
        </div>
      )}

      {!timeUp && busy !== "finish" && question && (
        <QuestionBody
          key={question.id}
          question={question}
          answer={answer}
          onAnswer={typing}
          rows={5}
          disabled={!!feedback || busy !== null}
          tag={returning ? <span className="chip border-ink-400 text-ink-200">Skipped earlier</span> : undefined}
          actions={
            <div className="space-y-3">
              {feedback && <InstantVerdict f={feedback} />}
              <div className="flex flex-wrap items-center gap-3">
                {!feedback ? (
                  <>
                    <button type="button" className="btn-primary" onClick={submit} disabled={!answer.trim() || busy !== null} data-testid="quiz-submit">
                      {busy === "submit" ? "Checking…" : <>{initial.instant ? "Check" : others ? "Save & next" : "Save & finish"} <span className="btn-arrow">→</span></>}
                    </button>
                    {others > 0 && (
                      <button type="button" className="btn-ghost" onClick={skip} disabled={busy !== null} data-testid="quiz-skip">
                        Skip for now ↷
                      </button>
                    )}
                  </>
                ) : (
                  <button type="button" className="btn-primary" onClick={afterFeedback} data-testid="quiz-next">
                    {ending.current || !others ? "See results" : "Next"} <span className="btn-arrow">→</span>
                  </button>
                )}
                <span className="ml-auto">
                  {!confirmEnd ? (
                    <button type="button" className="font-mono text-[12px] text-ink-500 underline-offset-4 hover:text-ink-200 hover:underline" onClick={() => setConfirmEnd(true)}>
                      Finish now
                    </button>
                  ) : (
                    <span className="flex items-center gap-2 font-mono text-[12px]">
                      <span className="text-ink-400">End with {initial.length - answered} left?</span>
                      <button type="button" className="text-signal underline-offset-4 hover:underline" onClick={() => end()} data-testid="quiz-finish">Yes, finish</button>
                      <button type="button" className="text-ink-400 hover:text-ink-100" onClick={() => setConfirmEnd(false)}>No</button>
                    </span>
                  )}
                </span>
              </div>
            </div>
          }
        />
      )}
    </div>
  );
}

function TimerBar({ label, n, total, answered, left, frac, urgent, slots, cur, instant }: {
  label: string; n: number; total: number; answered: number; left: number; frac: number; urgent: boolean; slots: QuizSlot[]; cur: number | null; instant: boolean;
}) {
  const [top, setTop] = useState(0);
  useEffect(() => {
    // Sit just under the site header, whatever height it wraps to.
    const header = document.querySelector("header");
    if (!header) return;
    const set = () => setTop(header.getBoundingClientRect().height);
    set();
    const ro = new ResizeObserver(set);
    ro.observe(header);
    return () => ro.disconnect();
  }, []);
  return (
    <div className="sticky z-30 -mx-4 border-b border-ink-700 bg-ink-950/95 px-4 pb-3 pt-3 backdrop-blur sm:-mx-6 sm:px-6" style={{ top }} data-testid="quiz-timer" data-urgent={urgent ? "1" : "0"}>
      <div className="flex items-center gap-4">
        <div className="min-w-0 flex-1">
          <div className="label truncate">{label} · {instant ? "feedback after each" : "feedback at the end"}</div>
          <div className="mt-0.5 flex items-baseline gap-2">
            <span className="font-display text-2xl font-bold tabular-nums text-ink-50" data-testid="quiz-counter">
              Question {n}<span className="text-ink-500">/{total}</span>
            </span>
            <span className="font-mono text-[11px] text-ink-500 max-sm:hidden">{answered} answered</span>
          </div>
        </div>
        <div className={`text-right ${urgent ? "text-signal" : "text-ink-50"}`}>
          <div className={`font-mono text-[34px] font-semibold leading-none tabular-nums ${urgent ? "timer-urgent" : ""}`} data-testid="quiz-clock" aria-label={`${mmss(left)} left`}>
            {mmss(left)}
          </div>
          <div className="mt-1 font-mono text-[10px] uppercase tracking-wider text-ink-500">left</div>
        </div>
      </div>
      <div className="mt-3 h-1 bg-ink-800" aria-hidden="true">
        <div className={`h-full transition-[width] duration-300 ease-linear ${urgent ? "bg-signal" : "bg-accent"}`} style={{ width: `${frac * 100}%` }} />
      </div>
      <ol className="mt-2 flex gap-1" aria-label="Questions">
        {slots.map((s) => (
          <li
            key={s.position}
            title={`Question ${s.position + 1}: ${s.state}`}
            className={`h-1.5 flex-1 ${
              s.position === cur ? "bg-ink-100" :
              s.verdict === "correct" ? "bg-accent" :
              s.verdict ? "bg-signal" :
              s.state === "answered" ? "bg-accent/60" :
              s.state === "skipped" ? "border border-dashed border-ink-500" : "bg-ink-800"
            }`}
          />
        ))}
      </ol>
    </div>
  );
}

const VERDICT: Record<FeedbackPayload["verdict"], [string, string]> = {
  correct: ["Right", "border-accent bg-accent/10 text-accent"],
  partially_correct: ["Partly right", "border-ink-300 bg-ink-900 text-ink-100"],
  incorrect: ["Not quite", "border-signal bg-signal/10 text-signal"],
};

function InstantVerdict({ f }: { f: FeedbackPayload }) {
  const [word, tone] = VERDICT[f.verdict];
  const answer = f.accepted_answers?.[0] || f.reference_answer;
  const raw = f.misconceptions[0]?.explanation || (f.missed_concepts[0] ? `Missed: ${f.missed_concepts[0]}` : "");
  // Don't repeat the answer line in other words.
  const why = answer && raw.includes(answer) && raw.length < answer.length + 40 ? "" : raw;
  return (
    <div className={`rise border px-4 py-3 ${tone}`} role="status" data-testid="instant-verdict">
      <div className="font-display text-lg font-semibold">{word}</div>
      {f.verdict !== "correct" && answer && (
        <p className="mt-1 text-[13px] text-ink-200"><span className="text-ink-500">Answer: </span><span className="break-words font-mono">{answer}</span></p>
      )}
      {f.verdict !== "correct" && why && <p className="mt-1 text-[13px] text-ink-300">{why}</p>}
    </div>
  );
}
