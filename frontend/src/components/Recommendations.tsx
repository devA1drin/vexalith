"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, LANGUAGE_IDS, type Language, type RecommendationsOut } from "@/lib/api";

const LEVEL_N: Record<string, number> = { beginner: 1, intermediate: 2, advanced: 3 };

function Dots({ level }: { level: string }) {
  const n = LEVEL_N[level] ?? 1;
  return (
    <span className="inline-flex gap-0.5" title={level} aria-label={level}>
      {[1, 2, 3].map((i) => <span key={i} className={`inline-block h-1.5 w-1.5 ${i <= n ? "bg-accent" : "bg-ink-700"}`} />)}
    </span>
  );
}

/** "Recommended for you": weakest skills, languages to revisit and unseen next questions. */
export function Recommendations({ index = "03" }: { index?: string }) {
  const [data, setData] = useState<RecommendationsOut | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("vexalith_language");
    const lang = LANGUAGE_IDS.includes(saved as Language) ? (saved as Language) : null;
    api.recommendations(lang).then(setData).catch(() => setFailed(true));
  }, []);

  if (failed) return null;
  if (!data) return <div className="card h-56 animate-pulse" aria-hidden="true" />;

  return (
    <section aria-labelledby="rec-h" className="card" data-testid="recommendations">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ink-700 px-5 py-3">
        <h2 id="rec-h" className="label">{index} · Recommended for you</h2>
        <span className="label text-ink-500">based on your answers · {data.language}</span>
      </div>
      <p className="px-5 pt-4 font-display text-xl font-semibold text-ink-50">{data.headline}</p>
      <div className="grid gap-px bg-ink-800 md:grid-cols-2">
        <div className="bg-ink-900 p-5">
          <div className="label mb-3">Skills to strengthen</div>
          <ol className="space-y-4">
            {data.topics.map((t) => {
              const pct = Math.round(t.mastery * 100);
              return (
                <li key={t.domain_slug} className="grid grid-cols-[1fr_auto] items-start gap-3" data-topic={t.domain_slug}>
                  <div className="min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-ink-50">{t.domain_name}</span>
                      <span className="font-mono text-[11px] text-ink-400">{t.attempts ? `${pct}%` : "new"}</span>
                    </div>
                    <span className="mt-1.5 block h-1 bg-ink-800" aria-hidden="true">
                      <span className="block h-full bg-accent" style={{ width: `${Math.max(pct, 2)}%` }} />
                    </span>
                    <p className="mt-1.5 text-[13px] text-ink-400">{t.reason}</p>
                  </div>
                  <Link
                    href={`/practice?language=${data.language}&topic=${t.domain_slug}`}
                    className="btn-ghost whitespace-nowrap px-3 py-1.5 text-[11px]"
                  >
                    Practise <span className="btn-arrow">→</span>
                  </Link>
                </li>
              );
            })}
          </ol>
        </div>
        <div className="bg-ink-900 p-5">
          <div className="label mb-3">Try next</div>
          {data.next_questions.length === 0 ? (
            <p className="text-sm text-ink-400">You have seen every question here. Switch language or pick a harder level.</p>
          ) : (
            <ul className="divide-y divide-ink-800 border-y border-ink-800">
              {data.next_questions.map((q) => (
                <li key={q.id}>
                  <Link
                    href={`/practice?language=${data.language}&question=${q.id}`}
                    className="group flex items-center gap-3 py-2.5 transition-colors hover:bg-ink-800/60"
                    data-next-question={q.id}
                  >
                    <span className="font-mono text-[11px] text-ink-500">#{String(q.id).padStart(3, "0")}</span>
                    <span className="min-w-0 flex-1 truncate text-ink-100 group-hover:text-ink-50">{q.title}</span>
                    <span className="hidden font-mono text-[11px] uppercase tracking-wider text-ink-500 sm:inline">{q.domain_name}</span>
                    <Dots level={q.difficulty} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {data.languages.length > 0 && (
            <>
              <div className="label mb-2 mt-5">Languages to revisit</div>
              <ul className="space-y-1.5">
                {data.languages.map((l) => (
                  <li key={l.language} className="flex items-baseline justify-between gap-3 text-sm">
                    <Link href={`/practice?language=${l.language}`} className="font-mono text-[12px] uppercase tracking-wider text-accent hover:underline">
                      {l.name}
                    </Link>
                    <span className="text-ink-400">{l.reason}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
