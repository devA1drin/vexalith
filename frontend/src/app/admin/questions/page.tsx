"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AdminHeading, Notice, Pager } from "@/components/admin/AdminShell";
import { RateBar } from "@/components/admin/Charts";
import { AdminSelect, Pips } from "@/components/admin/Field";
import { adminApi, type QuestionsOut } from "@/lib/adminApi";
import { adminQuery, ratingBand } from "@/lib/adminFormat";

type F = { topic: string; language: string; difficulty: string; kind: string; status: string; sort: string; q: string; page: number };
const EMPTY: F = { topic: "", language: "", difficulty: "", kind: "", status: "", sort: "id", q: "", page: 1 };

export default function AdminQuestions() {
  const [f, setF] = useState<F | null>(null);
  const [text, setText] = useState("");
  const [data, setData] = useState<QuestionsOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const init = { ...EMPTY };
    for (const k of Object.keys(EMPTY) as (keyof F)[]) {
      const v = p.get(k);
      if (v) (init as Record<string, string | number>)[k] = k === "page" ? Number(v) || 1 : v;
    }
    setF(init);
    setText(init.q);
  }, []);

  useEffect(() => {
    if (!f) return;
    const t = setTimeout(() => setF((x) => (x && x.q !== text ? { ...x, q: text, page: 1 } : x)), 250);
    return () => clearTimeout(t);
  }, [text, f]);

  useEffect(() => {
    if (!f) return;
    window.history.replaceState(null, "", `/admin/questions${adminQuery({ ...f, sort: f.sort === "id" ? "" : f.sort })}`);
    adminApi.questions(f).then(setData).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load questions."));
  }, [f]);

  const set = (k: keyof F) => (v: string) => setF((x) => (x ? { ...x, [k]: v, page: 1 } : x));
  if (!f) return null;

  return (
    <div className="space-y-6" data-testid="admin-questions">
      <AdminHeading
        kicker="Questions"
        title="Question bank"
        actions={<Link href="/admin/questions/new" className="btn-primary">New question <span className="btn-arrow">+</span></Link>}
      >
        Pass rate is the share of answers graded right. Rating is Elo-style: it starts at the question&apos;s level and climbs when learners who usually get things right miss it.
      </AdminHeading>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <div className="col-span-2 md:col-span-3 xl:col-span-2">
          <label className="flex min-w-0 flex-col gap-1">
            <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">Search</span>
            <input className="input py-1.5" type="search" placeholder="Title, text or #id" value={text} onChange={(e) => setText(e.target.value)} data-testid="question-search" />
          </label>
        </div>
        <AdminSelect label="Topic" value={f.topic} onChange={set("topic")} options={(data?.topics ?? []).map((t) => [t.slug, t.name])} />
        <AdminSelect label="Language" value={f.language} onChange={set("language")} options={(data?.languages ?? []).map((l) => [l.key, l.label])} />
        <AdminSelect label="Level" value={f.difficulty} onChange={set("difficulty")} options={[["beginner", "Beginner"], ["intermediate", "Intermediate"], ["advanced", "Advanced"]]} />
        <AdminSelect label="Kind" value={f.kind} onChange={set("kind")} options={[["explain", "Explain"], ["fill_blank", "Fill in the code"]]} />
        <AdminSelect label="Status" value={f.status} onChange={set("status")} options={[["visible", "Live"], ["hidden", "Hidden"], ["edited", "Edited"], ["new", "Added here"]]} />
        <AdminSelect label="Sort" value={f.sort} onChange={set("sort")} all={null} options={[["id", "Number"], ["attempts", "Most attempts"], ["fail_rate", "Most missed"], ["pass_rate", "Best pass rate"], ["rating", "Highest rating"]]} />
      </div>

      {error && <Notice tone="error">{error}</Notice>}
      {data && (
        <>
          <div className="card">
            <div className="hidden grid-cols-[3.5rem_minmax(0,1fr)_9rem_3.5rem_5rem_7.5rem_5.5rem] gap-4 border-b border-ink-700 px-4 py-2 lg:grid">
              {["#", "Question", "Topic", "Level", "Attempts", "Pass rate", "Rating"].map((h) => <span key={h} className="label">{h}</span>)}
            </div>
            {data.items.length === 0 && <p className="px-4 py-6 text-[14px] text-ink-400">No questions match these filters.</p>}
            <ul>
              {data.items.map((q) => (
                <li key={q.id} className={`border-b border-ink-800 last:border-0 ${q.hidden ? "bg-ink-950/60" : ""}`} data-testid="question-row">
                  <Link href={`/admin/questions/${q.id}`} className="grid grid-cols-[3rem_minmax(0,1fr)] gap-x-3 gap-y-1.5 px-4 py-3 hover:bg-ink-800/40 lg:grid-cols-[3.5rem_minmax(0,1fr)_9rem_3.5rem_5rem_7.5rem_5.5rem] lg:items-center lg:gap-4">
                    <span className="font-mono text-[12px] text-ink-500">#{q.id}</span>
                    <span className="min-w-0">
                      <span className="flex min-w-0 items-center gap-2">
                        <span className={`truncate text-[14px] ${q.hidden ? "text-ink-400 line-through decoration-ink-600" : "text-ink-50"}`}>{q.title}</span>
                        {q.hidden && <span className="chip shrink-0 border-signal px-1.5 text-[10px] text-signal-soft">Hidden</span>}
                        {q.edited && <span className="chip shrink-0 border-accent/60 px-1.5 text-[10px] text-accent">Edited</span>}
                        {q.source === "admin" && <span className="chip shrink-0 px-1.5 text-[10px]">Added</span>}
                        {q.kind === "fill_blank" && <span className="chip shrink-0 px-1.5 text-[10px]">Fill-in</span>}
                      </span>
                      <span className="block truncate text-[12px] text-ink-500">{q.preview}</span>
                    </span>
                    <span className="col-start-2 truncate font-mono text-[11px] text-ink-400 lg:col-start-auto">{q.topic_label} · {q.language_label}</span>
                    <span className="col-start-2 flex flex-wrap items-center gap-x-4 gap-y-1 lg:contents">
                      <Pips level={q.difficulty} />
                      <span className="font-mono text-[12px] text-ink-300">{q.attempts ?? 0}<span className="lg:hidden text-ink-500"> attempts</span></span>
                      <RateBar value={q.pass_rate} />
                      <span className="font-mono text-[12px] text-ink-300" title={`Elo-style rating: ${ratingBand(q.rating ?? 0)}`}>◆ {q.rating}</span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <Pager page={data.page} pages={data.pages} total={data.total} onPage={(p) => setF((x) => (x ? { ...x, page: p } : x))} noun="questions" />
        </>
      )}
    </div>
  );
}
