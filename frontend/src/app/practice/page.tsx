"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError, DIFFICULTY_IDS, LANGUAGE_IDS, type Difficulty, type FeedbackPayload, type Focus, type Language, type PracticeOptions, type Question } from "@/lib/api";
import { CodeBlock } from "@/components/CodeBlock";
import { FeedbackCard } from "@/components/FeedbackCard";
import { HintPanel } from "@/components/HintPanel";

const LANG_KEY = "vexalith_language";
const FOCUS_KEY = "vexalith_focus";
const LEVEL_KEY = "vexalith_level";
const LEVELS: { id: Difficulty; label: string; hint: string }[] = [
  { id: "adaptive", label: "Adaptive", hint: "Vexalith picks the level from your results (recommended)" },
  { id: "beginner", label: "Beginner", hint: "Only level-1 questions" },
  { id: "intermediate", label: "Intermediate", hint: "Only level-2 questions" },
  { id: "advanced", label: "Advanced", hint: "Only level-3 questions" },
];
const TOPIC_NAMES: Record<string, string> = {
  fundamentals: "Fundamentals", code_tracing: "Code Tracing", debugging: "Debugging",
  algorithmic_thinking: "Algorithmic Thinking", edge_cases_testing: "Edge Cases & Testing",
  code_review_design: "Code Review & Design", data_structures: "Data Structures",
  oop: "Object-Oriented Programming", algorithms: "Algorithms", logic_problems: "Logic Problems",
};
const LANGS: { id: Language; label: string }[] = [
  { id: "python", label: "Python" },
  { id: "javascript", label: "JavaScript" },
  { id: "php", label: "PHP" },
  { id: "cpp", label: "C++" },
  { id: "java", label: "Java" },
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
  const [focus, setFocus] = useState<Focus | null>(null);
  const focusRef = useRef<Focus | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>("adaptive");
  const [topic, setTopic] = useState<string | null>(null);
  const optsRef = useRef<{ difficulty: Difficulty; topic: string | null }>({ difficulty: "adaptive", topic: null });
  const [dailyId, setDailyId] = useState<number | null>(null);
  const opts = (): PracticeOptions => ({ focus: focusRef.current, ...optsRef.current });
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
        show(await api.nextQuestion(lang, recent.current, opts()));
      } catch (e) {
        handleError(e, "Failed to load question");
      } finally {
        setBusy(null);
      }
    },
    [show],
  );

  useEffect(() => {
    api.daily().then((d) => setDailyId(d.question_id)).catch(() => {});
  }, []);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    // Links from recommendations / the daily challenge: ?language=&level=&topic=&question=
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get("language");
    const saved = LANGUAGE_IDS.includes(urlLang as Language) ? urlLang : localStorage.getItem(LANG_KEY);
    const lang: Language = LANGUAGE_IDS.includes(saved as Language) ? (saved as Language) : "python";
    setLanguage(lang);
    if (urlLang === lang) localStorage.setItem(LANG_KEY, lang);
    const f: Focus | null = localStorage.getItem(FOCUS_KEY) === "fundamentals" ? "fundamentals" : null;
    focusRef.current = f;
    setFocus(f);
    const urlLevel = params.get("level");
    if (DIFFICULTY_IDS.includes(urlLevel as Difficulty)) localStorage.setItem(LEVEL_KEY, urlLevel as string);
    const savedLevel = localStorage.getItem(LEVEL_KEY) as Difficulty | null;
    const lvl: Difficulty = savedLevel && DIFFICULTY_IDS.includes(savedLevel) ? savedLevel : "adaptive";
    const tp = params.get("topic");
    const t = tp && tp in TOPIC_NAMES ? tp : null;
    optsRef.current = { difficulty: lvl, topic: t };
    setDifficulty(lvl);
    setTopic(t);
    const qid = Number(params.get("question"));
    if (Number.isInteger(qid) && qid > 0) {
      setBusy("load");
      api.question(qid).then(show).catch(() => loadNext(lang)).finally(() => setBusy(null));
    } else {
      loadNext(lang);
    }
  }, [loadNext, show]);

  async function onSkip() {
    if (!question) return;
    setBusy("skip");
    setError(null);
    setLeaving(true);
    try {
      const res = await api.skip(question.id, language, opts());
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

  function onDifficulty(d: Difficulty) {
    if (d === difficulty) return;
    setDifficulty(d);
    optsRef.current = { ...optsRef.current, difficulty: d };
    localStorage.setItem(LEVEL_KEY, d);
    if (!feedback) loadNext(language);
  }

  function onTopic(next: string | null) {
    const valid = next && next in TOPIC_NAMES ? next : null;
    if (valid === topic) return;
    setTopic(valid);
    optsRef.current = { ...optsRef.current, topic: valid };
    window.history.replaceState(null, "", valid ? `/practice?topic=${valid}` : "/practice");
    if (!feedback) loadNext(language);
  }

  function clearTopic() {
    onTopic(null);
  }

  function onFocusToggle() {
    const next: Focus | null = focus ? null : "fundamentals";
    focusRef.current = next;
    setFocus(next);
    if (next) localStorage.setItem(FOCUS_KEY, next);
    else localStorage.removeItem(FOCUS_KEY);
    // Switch immediately unless the learner is reading feedback on an answer.
    if (next && !feedback && question?.domain_slug !== "fundamentals") loadNext(language);
  }

  const level = question ? LEVEL[question.difficulty] ?? 1 : 0;
  const isBlank = question?.kind === "fill_blank";
  const minChars = isBlank ? 1 : 10;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">01 · Practice{count > 0 && ` · drill ${String(count).padStart(2, "0")}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Reason it out.</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="grid grid-cols-3 gap-px border border-ink-700 bg-ink-700 sm:grid-cols-8"
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
                title={l.id === "general" ? "Language-agnostic logic and algorithm problems" : l.id === "cpp" ? "Modern C++ (C++17)" : l.id === "java" ? "Modern Java (Java 17)" : undefined}
                className={`px-3 py-1.5 ${l.id === "general" ? "max-sm:col-span-2" : ""} font-mono text-[12px] uppercase tracking-wider transition-colors ${
                  language === l.id ? "bg-accent text-ink-950" : "bg-ink-950 text-ink-300 hover:text-ink-50"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={onFocusToggle}
            disabled={busy !== null}
            aria-pressed={focus === "fundamentals"}
            data-testid="focus-fundamentals"
            title="Practice only Fundamentals"
            className={`flex items-center gap-2 border px-3 py-1.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${
              focus ? "border-accent text-accent" : "border-ink-700 text-ink-300 hover:text-ink-50"
            }`}
          >
            <span aria-hidden="true" className={`inline-block h-2.5 w-2.5 border ${focus ? "border-accent bg-accent" : "border-ink-500"}`} />
            Focus: Fundamentals
          </button>
          {!feedback && (
            <button type="button" onClick={onSkip} disabled={!question || busy !== null} className="btn-ghost py-[7px]" data-testid="skip">
              {busy === "skip" ? "Skipping…" : <>Skip <span className="btn-arrow">↷</span></>}
            </button>
          )}
        </div>
      </div>

      <div className="-mt-1 flex flex-wrap items-center gap-x-4 gap-y-2">
        <span className="label">Level</span>
        <div className="grid grid-cols-2 gap-px border border-ink-700 bg-ink-700 sm:grid-cols-4" role="radiogroup" aria-label="Difficulty level" data-testid="level-picker">
          {LEVELS.map((l, i) => (
            <button
              key={l.id}
              type="button"
              role="radio"
              aria-checked={difficulty === l.id}
              onClick={() => onDifficulty(l.id)}
              disabled={busy !== null}
              title={l.hint}
              data-level={l.id}
              className={`flex items-center gap-2 px-3 py-1.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${
                difficulty === l.id ? "bg-ink-100 text-ink-950" : "bg-ink-950 text-ink-300 hover:text-ink-50"
              }`}
            >
              {i === 0 ? (
                <span aria-hidden="true" className="text-[11px]">◐</span>
              ) : (
                <span aria-hidden="true" className="flex gap-0.5">
                  {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-1.5 w-1.5 ${n <= i ? (difficulty === l.id ? "bg-ink-950" : "bg-accent") : difficulty === l.id ? "bg-ink-400" : "bg-ink-700"}`} />)}
                </span>
              )}
              {l.label}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2">
          <span className="label">Topic</span>
          <select
            aria-label="Topic"
            data-testid="topic-select"
            value={topic ?? ""}
            onChange={(e) => onTopic(e.target.value || null)}
            disabled={busy !== null}
            className="border border-ink-700 bg-ink-950 px-2.5 py-1.5 font-mono text-[12px] text-ink-100 focus:border-accent focus:outline-none"
          >
            <option value="">All topics (adaptive)</option>
            {Object.entries(TOPIC_NAMES).map(([slug, label]) => (
              <option key={slug} value={slug}>{label}</option>
            ))}
          </select>
        </label>
        {difficulty === "adaptive" && !topic && <span className="font-mono text-[11px] text-ink-500">level follows your results</span>}
        {topic && (
          <span className="chip gap-2 border-accent text-accent" data-testid="topic-chip">
            Topic: {TOPIC_NAMES[topic] ?? topic}
            <button type="button" onClick={clearTopic} aria-label="Clear topic" className="text-ink-300 hover:text-ink-50">×</button>
          </span>
        )}
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
            {question.id === dailyId && (
              <span className="chip border-accent bg-accent text-ink-950" data-testid="daily-chip">
                Daily challenge
              </span>
            )}
            {isBlank && (
              <span className="chip border-accent text-accent" data-testid="kind-fill-blank">
                Missing code
              </span>
            )}
            <span className="label ml-auto">#{String(question.id).padStart(3, "0")}</span>
          </div>
          <div className="grid gap-6 p-4 sm:p-6 lg:grid-cols-2">
            <div className="min-w-0 space-y-4">
              <h2 className="font-display text-2xl font-semibold leading-tight text-ink-50" data-testid="question-title">{question.title}</h2>
              <CodeBlock code={question.code} language={question.language} />
            </div>
            <div className="flex min-w-0 flex-col gap-4">
              <p className="border-l-2 border-accent pl-4 text-[17px] font-medium leading-relaxed text-ink-50">{question.prompt}</p>
              <HintPanel questionId={question.id} hintCount={question.hint_count ?? 0} locked={!!feedback} />
              <label className="flex flex-1 flex-col gap-2">
                <span className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="label">{isBlank ? "The missing code (+ why, optional)" : "Your explanation"}</span>
                  <span className="font-mono text-[11px] text-ink-500" data-testid="language-hint" lang="fil">English · Filipino · Taglish</span>
                </span>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  rows={8}
                  disabled={!!feedback || busy === "submit"}
                  placeholder={
                    isBlank
                      ? "Type the code that replaces the highlighted ? slot.\nThen, if you like, say why it fits (English, Filipino or Taglish)."
                      : "Answer first, then justify it.\ne.g. \"Line 5 prints … because …\"\nPuwede ring sumagot sa Filipino o Taglish."
                  }
                  className="input min-h-[11rem] flex-1 font-mono text-[13px] leading-6"
                />
              </label>
              <div className="flex flex-wrap items-center gap-3">
                {!feedback ? (
                  <button type="button" onClick={onSubmit} disabled={answer.trim().length < minChars || busy !== null} className="btn-primary" data-testid="submit">
                    {busy === "submit" ? "Evaluating…" : <>Submit <span className="btn-arrow">→</span></>}
                  </button>
                ) : (
                  <button type="button" onClick={() => loadNext(language)} disabled={busy !== null} className="btn-primary" data-testid="next">
                    {busy === "load" ? "Loading…" : <>Next question <span className="btn-arrow">→</span></>}
                  </button>
                )}
                <span className="font-mono text-[11px] text-ink-500">
                  {!feedback && (answer.trim().length < minChars ? `${answer.trim().length}/${minChars} min` : `${answer.trim().length} chars`)}
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
