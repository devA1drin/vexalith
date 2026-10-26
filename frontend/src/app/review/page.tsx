"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError, type FilterOption, type ReviewFilters, type ReviewItem, type ReviewOut } from "@/lib/api";
import { PageIntro } from "@/components/PageIntro";
import { PracticeTabs } from "@/components/PracticeTabs";
import { ago, LEVEL, until } from "@/lib/when";
import { FILTER_KEYS, filtersQuery, readFilters } from "@/lib/reviewFilters";


const PAGE = 8;

export default function ReviewPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<ReviewFilters | null>(null);
  const [data, setData] = useState<ReviewOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [shown, setShown] = useState(PAGE);

  useEffect(() => setFilters(readFilters(window.location.search)), []);

  const load = useCallback((f: ReviewFilters) => {
    api.review(f).then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/review";
      else setError(e instanceof Error ? e.message : "Couldn't load your mistakes.");
    });
  }, []);

  useEffect(() => {
    if (!filters) return;
    setShown(PAGE);
    window.history.replaceState(null, "", `/review${filtersQuery(filters)}`);
    load(filters);
  }, [filters, load]);

  const set = (k: keyof ReviewFilters, v: string) => setFilters((f) => ({ ...(f ?? {}), [k]: v || undefined }));
  const active = filters ? FILTER_KEYS.filter((k) => filters[k]).length : 0;

  const retry = async (item: ReviewItem) => {
    if (item.kind === "question") {
      router.push(`/review/practice${filtersQuery(filters ?? {}, { start: item.key })}`);
      return;
    }
    setBusy(item.key);
    try {
      await api.retryExercise(item.slug as string);
      router.push(`/code/${item.slug}?from=review`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't start the retry.");
      setBusy(null);
    }
  };

  const questions = data?.items.filter((i) => i.kind === "question").length ?? 0;
  const rules = data?.rules ?? { fix_xp: 5, confirm_days: 3, second_look: 10 };
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">01 · Practice · Review</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Fix what slipped.</h1>
        </div>
        {questions > 0 && (
          <Link href={`/review/practice${filtersQuery(filters ?? {})}`} className="btn-primary" data-testid="practice-mistakes">
            Practice my mistakes <span className="btn-arrow">→</span>
          </Link>
        )}
      </div>
      <PracticeTabs reviewCount={data ? data.counts.to_fix + data.counts.check_again : undefined} />
      <PageIntro>
        Questions you got wrong or only partly right, and coding exercises that failed or that you solved after seeing the answer.
        Get one right again here and it leaves the list. It comes back once, {rules.confirm_days} days later, to check it stuck.
      </PageIntro>

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-40 animate-pulse" />}
      {data && (
        <>
          <Summary data={data} />
          <div className="panel space-y-3 p-4" data-testid="review-filters">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="label">Filter</span>
              <div className="flex flex-wrap items-center gap-3">
                <KindTabs value={filters?.kind ?? ""} onChange={(v) => set("kind", v)} />
                {active > 0 && (
                  <button type="button" className="font-mono text-[12px] text-ink-400 underline-offset-4 hover:text-accent hover:underline" onClick={() => setFilters({})}>
                    Clear filters
                  </button>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <Select label="Topic" value={filters?.topic} options={data.filters.topics} onChange={(v) => set("topic", v)} />
              <Select label="Language" value={filters?.language} options={data.filters.languages} onChange={(v) => set("language", v)} />
              <Select label="Path" value={filters?.path} options={data.filters.paths} onChange={(v) => set("path", v)} />
              <Select label="Difficulty" value={filters?.difficulty} options={data.filters.difficulties} onChange={(v) => set("difficulty", v)} />
            </div>
          </div>

          {data.items.length === 0 ? (
            <Empty filtered={active > 0} anyOpen={data.counts.to_fix + data.counts.check_again > 0} onClear={() => setFilters({})} />
          ) : (
            <ul className="space-y-3" data-testid="review-list">
              {data.items.slice(0, shown).map((it, i) => (
                <ItemCard key={it.key} item={it} i={i % PAGE} busy={busy === it.key} onRetry={() => retry(it)} />
              ))}
            </ul>
          )}
          {data.items.length > shown && (
            <button type="button" className="btn-ghost w-full justify-center" onClick={() => setShown((n) => n + PAGE)} data-testid="show-more">
              Show {Math.min(PAGE, data.items.length - shown)} more · {data.items.length - shown} left
            </button>
          )}

          {data.coming_back.length > 0 && (
            <section className="space-y-3" data-testid="coming-back">
              <h2 className="label">Coming back to check it stuck</h2>
              <ul className="divide-y divide-ink-800 border border-ink-700">
                {data.coming_back.map((c) => (
                  <li key={c.key} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 px-4 py-2.5">
                    <span className="min-w-0 break-words text-[14px] text-ink-200">{c.title}</span>
                    <span className="font-mono text-[12px] text-ink-400">fixed {ago(c.fixed_at)} · back {until(c.due_at)}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <p className="font-mono text-[12px] text-ink-500">
            +{rules.fix_xp} XP the first time you fix each item here · fixing {rules.second_look} earns the Second Look badge
          </p>
        </>
      )}
    </div>
  );
}

function Summary({ data }: { data: ReviewOut }) {
  const { counts, fixes, rules } = data;
  const pct = Math.min(100, Math.round((fixes / rules.second_look) * 100));
  const cells = [
    { n: counts.to_fix, label: "To fix", tone: counts.to_fix ? "text-signal" : "text-ink-50" },
    { n: counts.check_again, label: "Check again", tone: counts.check_again ? "text-accent" : "text-ink-50" },
    { n: counts.waiting, label: "Coming back", tone: "text-ink-50" },
    { n: counts.done, label: "Done for good", tone: "text-ink-50" },
  ];
  return (
    <div className="grid grid-cols-2 gap-px border border-ink-700 bg-ink-700 md:grid-cols-5" data-testid="review-summary">
      {cells.map((c) => (
        <div key={c.label} className="bg-ink-950 p-4">
          <div className={`font-display text-3xl font-bold tabular-nums ${c.tone}`}>{c.n}</div>
          <div className="label mt-1">{c.label}</div>
        </div>
      ))}
      <div className="col-span-2 bg-ink-950 p-4 md:col-span-1">
        <div className="flex items-baseline justify-between gap-2">
          <span className="font-display text-3xl font-bold tabular-nums text-ink-50">{Math.min(fixes, rules.second_look)}<span className="text-ink-500">/{rules.second_look}</span></span>
        </div>
        <div className="label mt-1">Fixes to Second Look</div>
        <div className="mt-2 h-1.5 bg-ink-800"><div className="h-full bg-accent" style={{ width: `${pct}%` }} /></div>
      </div>
    </div>
  );
}

function KindTabs({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const opts = [
    ["", "All"],
    ["question", "Questions"],
    ["exercise", "Code"],
  ];
  return (
    <div role="radiogroup" aria-label="Type" className="flex border border-ink-700">
      {opts.map(([v, l]) => (
        <button
          key={v}
          type="button"
          role="radio"
          aria-checked={value === v}
          onClick={() => onChange(v)}
          className={`px-3 py-1 font-mono text-[12px] uppercase tracking-wider ${value === v ? "bg-accent text-ink-950" : "text-ink-300 hover:text-ink-50"}`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}

function Select({ label, value, options, onChange }: { label: string; value?: string; options: FilterOption[]; onChange: (v: string) => void }) {
  return (
    <label className="flex min-w-0 flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">{label}</span>
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className={`input w-full min-w-0 py-1.5 text-[13px] ${value ? "border-accent text-ink-50" : ""}`}
        data-testid={`filter-${label.toLowerCase()}`}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label} ({o.count})
          </option>
        ))}
      </select>
    </label>
  );
}

const REASON_TONE: Record<ReviewItem["reason"], string> = {
  wrong: "border-signal text-signal",
  timeout: "border-signal text-signal",
  failed: "border-signal text-signal",
  partial: "border-ink-400 text-ink-200",
  helped: "border-ink-400 text-ink-200",
};

function ItemCard({ item, i, busy, onRetry }: { item: ReviewItem; i: number; busy: boolean; onRetry: () => void }) {
  const level = LEVEL[item.difficulty] ?? 1;
  const check = item.status === "check_again";
  return (
    <li
      className={`rise card relative overflow-hidden border-l-2 ${check ? "border-l-accent" : "border-l-signal"}`}
      style={{ ["--rd" as string]: `${Math.min(i, 8) * 35}ms` }}
      data-testid={`review-item-${item.key}`}
      data-status={item.status}
    >
      <div className="flex flex-wrap items-center gap-2 border-b border-ink-800 px-4 py-2.5 sm:px-5">
        {check ? (
          <span className="chip border-accent bg-accent text-ink-950">Check again</span>
        ) : (
          <span className={`chip ${REASON_TONE[item.reason]}`}>{item.reason_label}</span>
        )}
        <span className="chip text-ink-100">{item.kind === "exercise" ? `Code · ${item.topic_name}` : item.topic_name}</span>
        <span className="chip uppercase">{item.language}</span>
        <span className="chip gap-1.5" title={item.difficulty}>
          {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
        </span>
        <span className="ml-auto font-mono text-[11px] text-ink-500">
          {check ? `fixed ${ago(item.fixed_at)}` : `${item.times_wrong > 1 ? `missed ${item.times_wrong}× · ` : ""}${ago(item.last_wrong_at)}`}
        </span>
      </div>
      <div className="grid gap-4 p-4 sm:p-5 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0 space-y-2">
          <h3 className="font-display text-lg font-semibold leading-snug text-ink-50">{item.title}</h3>
          <div>
            <div className="label mb-1">{item.kind === "exercise" ? "Your last code" : "Your last answer"}</div>
            {item.last_answer ? (
              <pre className="max-h-32 overflow-hidden whitespace-pre-wrap break-words border border-ink-800 bg-ink-900 px-3 py-2 font-mono text-[12px] leading-5 text-ink-300">
                {item.last_answer}
              </pre>
            ) : (
              <p className="font-mono text-[12px] text-ink-500">{item.reason === "timeout" ? "No answer — time ran out." : "No answer saved."}</p>
            )}
            {item.tests && <p className="mt-1 font-mono text-[11px] text-ink-500">{item.tests[0]} of {item.tests[1]} tests passed</p>}
          </div>
        </div>
        <div className="flex min-w-0 flex-col gap-3">
          {item.feedback && (
            <div>
              <div className="label mb-1">What went wrong</div>
              <p className="text-[14px] leading-relaxed text-ink-200">{item.feedback}</p>
            </div>
          )}
          {item.explanation && (
            <div className="border-l-2 border-accent/60 pl-3">
              <div className="label mb-1">The idea</div>
              <p className="text-[14px] leading-relaxed text-ink-300">{item.explanation}</p>
            </div>
          )}
          <div className="mt-auto flex flex-wrap items-center gap-3 pt-1">
            <button type="button" onClick={onRetry} disabled={busy} className="btn-primary py-[7px]" data-testid="retry">
              {busy ? "Opening…" : <>{check ? "Check it" : "Retry"} <span className="btn-arrow">→</span></>}
            </button>
            <span className="font-mono text-[11px] text-ink-500">{check ? "Right again = done for good" : "Get it right = fixed"}</span>
          </div>
        </div>
      </div>
    </li>
  );
}

function Empty({ filtered, anyOpen, onClear }: { filtered: boolean; anyOpen: boolean; onClear: () => void }) {
  return (
    <div className="card flex flex-col items-start gap-3 p-6" data-testid="review-empty">
      <h2 className="font-display text-2xl font-semibold text-ink-50">{filtered && anyOpen ? "Nothing matches these filters." : "Nothing to fix right now."}</h2>
      <p className="max-w-xl text-[14px] text-ink-300">
        {filtered && anyOpen
          ? "You still have mistakes in other topics."
          : "When you miss a question or an exercise beats you, it lands here so you can come back to it."}
      </p>
      <div className="flex flex-wrap gap-3">
        {filtered && anyOpen && <button type="button" className="btn-ghost" onClick={onClear}>Clear filters</button>}
        <Link href="/practice" className="btn-ghost">Practice</Link>
        <Link href="/quiz" className="btn-ghost">Timed quiz</Link>
      </div>
    </div>
  );
}
