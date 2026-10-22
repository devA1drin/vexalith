"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError, LANGUAGE_IDS, type FeedbackPayload, type Language, type Question } from "@/lib/api";
import { CodeBlock } from "@/components/CodeBlock";
import { FeedbackCard } from "@/components/FeedbackCard";

const LANG_KEY = "vexalith_language";
const LANGS: { id: Language; label: string }[] = [
  { id: "python", label: "Python" },
  { id: "javascript", label: "JavaScript" },
  { id: "php", label: "PHP" },
  { id: "html", label: "HTML" },
  { id: "css", label: "CSS" },
  { id: "general", label: "General" },
];
const LEVEL: Record<string, number> = { beginner: 1, intermediate: 2, advanced: 3 };

export default function PracticePage() {
  const [language, setLanguage] = useState<Language>("python");
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<null | "load" | "skip" | "submit">(null);
  const [leaving, setLeaving] = useState(false);
  const [count, setCount] = useState(0);
  const recent = useRef<number[]>([]);
  const initialized = useRef(false);

  const show = useCallback((q: Question) => {
    setQuestion(q);
    setAnswer("");
    setFeedback(null);
    setLeaving(false);
    setCount((c) => c + 1);
    recent.current = [q.id, ...recent.current.filter((id) => id !== q.id)].slice(0, 8);
  }, []);

  const handleError = (e: unknown, fallback: string) => {
    setLeaving(false);
    if (e instanceof ApiError && e.status === 401) {
      window.location.href = "/login?callbackUrl=/practice";
      return;
    }
    setError(e instanceof Error ? e.message : fallback);
  };

  const loadNext = useCallback(
    async (lang: Language) => {
      setBusy("load");
      setError(null);
      setLeaving(true);
      try {
        show(await api.nextQuestion(lang, recent.current));
      } catch (e) {
        handleError(e, "Failed to load question");
      } finally {
        setBusy(null);
      }
    },
    [show],
  );

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    const saved = localStorage.getItem(LANG_KEY);
    const lang: Language = LANGUAGE_IDS.includes(saved as Language) ? (saved as Language) : "python";
    setLanguage(lang);
    loadNext(lang);
  }, [loadNext]);

  async function onSkip() {
    if (!question) return;
    setBusy("skip");
    setError(null);
    setLeaving(true);
    try {
      const res = await api.skip(question.id, language);
      show(res.next_question);
    } catch (e) {
      handleError(e, "Skip failed");
    } finally {
      setBusy(null);
    }
  }

  async function onSubmit() {
    if (!question) return;
    setBusy("submit");
    setError(null);
    try {
      const res = await api.submitResponse(question.id, answer);
      setFeedback(res.feedback);
    } catch (e) {
      handleError(e, "Submit failed");
    } finally {
      setBusy(null);
    }
  }

  function onLanguage(lang: Language) {
    if (lang === language) return;
    setLanguage(lang);
    localStorage.setItem(LANG_KEY, lang);
    loadNext(lang);
  }

  const level = question ? LEVEL[question.difficulty] ?? 1 : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">01 · Practice{count > 0 && ` · drill ${String(count).padStart(2, "0")}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Reason it out.</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="grid grid-cols-3 gap-px border border-ink-700 bg-ink-700 sm:grid-cols-6"
            role="radiogroup"
            aria-label="Language"
          >
            {LANGS.map((l) => (
              <button
                key={l.id}
                type="button"
                role="radio"
                aria-checked={language === l.id}
                onClick={() => onLanguage(l.id)}
                disabled={busy !== null}
                data-lang={l.id}
                title={l.id === "general" ? "Language-agnostic logic and algorithm problems" : undefined}
                className={`px-3 py-1.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${
                  language === l.id ? "bg-accent text-ink-950" : "bg-ink-950 text-ink-300 hover:text-ink-50"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          {!feedback && (
            <button type="button" onClick={onSkip} disabled={!question || busy !== null} className="btn-ghost py-[7px]" data-testid="skip">
              {busy === "skip" ? "Skipping…" : <>Skip <span className="btn-arrow">↷</span></>}
            </button>
          )}
        </div>
      </div>

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}

      {!question && busy === "load" && <div className="card h-72 animate-pulse" />}

      {question && (
        <article
          key={`${question.id}-${count}`}
          className={`card ${leaving ? "q-leave" : "q-enter"}`}
          data-question-id={question.id}
          data-domain={question.domain_slug}
          data-language={question.language}
          aria-busy={leaving}
        >
          <div className="flex flex-wrap items-center gap-2 border-b border-ink-700 px-4 py-3 sm:px-6">
            <span className="chip text-ink-100">{question.domain_name}</span>
            <span className="chip gap-1.5" title={question.difficulty}>
              {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
              <span className="ml-1">{question.difficulty}</span>
            </span>
            <span className="label ml-auto">#{String(question.id).padStart(3, "0")}</span>
          </div>
          <div className="grid gap-6 p-4 sm:p-6 lg:grid-cols-2">
            <div className="min-w-0 space-y-4">
              <h2 className="font-display text-2xl font-semibold leading-tight text-ink-50" data-testid="question-title">{question.title}</h2>
              <CodeBlock code={question.code} language={question.language} />
            </div>
            <div className="flex min-w-0 flex-col gap-4">
              <p className="border-l-2 border-accent pl-4 text-[17px] font-medium leading-relaxed text-ink-50">{question.prompt}</p>
              <label className="flex flex-1 flex-col gap-2">
                <span className="label">Your explanation</span>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  rows={8}
                  disabled={!!feedback || busy === "submit"}
                  placeholder={"Answer first, then justify it.\ne.g. \"Line 5 prints … because …\""}
                  className="input min-h-[11rem] flex-1 font-mono text-[13px] leading-6"
                />
              </label>
              <div className="flex flex-wrap items-center gap-3">
                {!feedback ? (
                  <button type="button" onClick={onSubmit} disabled={answer.trim().length < 10 || busy !== null} className="btn-primary" data-testid="submit">
                    {busy === "submit" ? "Evaluating…" : <>Submit <span className="btn-arrow">→</span></>}
                  </button>
                ) : (
                  <button type="button" onClick={() => loadNext(language)} disabled={busy !== null} className="btn-primary" data-testid="next">
                    {busy === "load" ? "Loading…" : <>Next question <span className="btn-arrow">→</span></>}
                  </button>
                )}
                <span className="font-mono text-[11px] text-ink-500">
                  {!feedback && (answer.trim().length < 10 ? `${answer.trim().length}/10 min` : `${answer.trim().length} chars`)}
                </span>
              </div>
            </div>
          </div>
        </article>
      )}

      {feedback && <FeedbackCard feedback={feedback} />}
    </div>
  );
}
