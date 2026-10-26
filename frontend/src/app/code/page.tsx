"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api, ApiError, type CodeLanguage, type ExerciseList } from "@/lib/api";
import { PageIntro } from "@/components/PageIntro";
import { CODE_LANGUAGES, CODE_LANGUAGE_ORDER } from "@/lib/codeLanguages";

const LEVELS = ["beginner", "intermediate", "advanced"] as const;
const KEY = "vexalith_code_language";

export default function CodePage() {
  const [data, setData] = useState<ExerciseList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lang, setLang] = useState<CodeLanguage>("python");

  useEffect(() => {
    const saved = localStorage.getItem(KEY) as CodeLanguage | null;
    if (saved && saved in CODE_LANGUAGES) setLang(saved);
    api.exercises().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/code";
      else setError(e instanceof Error ? e.message : "Failed to load exercises");
    });
  }, []);

  const pick = (l: CodeLanguage) => {
    setLang(l);
    localStorage.setItem(KEY, l);
  };

  const list = useMemo(() => (data?.exercises ?? []).filter((e) => e.language === lang), [data, lang]);
  const solved = list.filter((e) => e.solved).length;
  const info = CODE_LANGUAGES[lang];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">02 · Code{data && ` · ${solved}/${list.length} solved in ${info.name}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Write it. Run it.</h1>
        </div>
      </div>
      <PageIntro steps={["Pick a language", "Open an exercise", "Write the function", "Run the tests, then Submit"]}>
        Small coding exercises with automatic tests. Your code runs inside your own browser, never on our server, so
        it&apos;s free and private. Each exercise has example tests you can see and a few hidden ones.
      </PageIntro>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Language">
        {CODE_LANGUAGE_ORDER.map((l) => {
          const count = data?.exercises.filter((e) => e.language === l).length;
          return (
            <button
              key={l}
              role="tab"
              aria-selected={lang === l}
              onClick={() => pick(l)}
              className={`chip px-3 py-1.5 text-[12px] transition-colors ${lang === l ? "border-accent bg-accent text-ink-950" : "hover:border-ink-400 hover:text-ink-50"}`}
              data-testid={`lang-${l}`}
            >
              {CODE_LANGUAGES[l].name}
              {count !== undefined && <span className={`ml-1.5 ${lang === l ? "text-ink-950/70" : "text-ink-500"}`}>{count}</span>}
            </button>
          );
        })}
      </div>

      <p className="font-mono text-[12px] text-ink-400" data-testid="engine-note">
        Runs in your browser on {info.engine} · {info.firstLoad}
      </p>

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-64 animate-pulse" />}

      {data &&
        LEVELS.map((level) => {
          const items = list.filter((e) => e.difficulty === level);
          if (!items.length) return null;
          return (
            <section key={level} className="space-y-3">
              <h2 className="label">{level}</h2>
              <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3" data-testid={`level-${level}`}>
                {items.map((e) => (
                  <li key={e.slug}>
                    <Link
                      href={`/code/${e.slug}`}
                      className="card group flex h-full flex-col gap-3 p-4 transition-colors hover:border-ink-400"
                      data-testid="exercise-card"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="chip">{e.topic}</span>
                        {e.solved ? (
                          <span className="font-mono text-[11px] uppercase tracking-wider text-accent">{e.solved_with_help ? "✓ With help" : "✓ Solved"}</span>
                        ) : e.attempted ? (
                          <span className="font-mono text-[11px] text-ink-400">{e.best_passed}/{e.tests} passed</span>
                        ) : null}
                      </div>
                      <span className="font-display text-lg font-semibold text-ink-50 group-hover:text-accent">{e.title}</span>
                      <span className="mt-auto font-mono text-[11px] text-ink-500">{e.tests} tests</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}
    </div>
  );
}
