"use client";

import { useEffect, useMemo, useState } from "react";
import { AdminHeading, Notice } from "@/components/admin/AdminShell";
import { RateBar } from "@/components/admin/Charts";
import { AdminSelect, Pips } from "@/components/admin/Field";
import { adminApi, type ExerciseRow } from "@/lib/adminApi";
import { num } from "@/lib/adminFormat";

export default function AdminExercises() {
  const [rows, setRows] = useState<ExerciseRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lang, setLang] = useState("");
  const [topic, setTopic] = useState("");
  const [level, setLevel] = useState("");
  const [sort, setSort] = useState("runs");
  useEffect(() => { adminApi.exercises().then((d) => setRows(d.items)).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load exercises.")); }, []);

  const shown = useMemo(() => {
    const r = (rows ?? []).filter((x) => (!lang || x.language === lang) && (!topic || x.topic === topic) && (!level || x.difficulty === level));
    const key = (x: ExerciseRow) => (sort === "solve_rate" ? (x.solve_rate ?? -1) : sort === "hard" ? -(x.solve_rate ?? 2) : x.runs);
    return [...r].sort((a, b) => key(b) - key(a) || a.title.localeCompare(b.title));
  }, [rows, lang, topic, level, sort]);

  const langs = useMemo(() => [...new Map((rows ?? []).map((r) => [r.language, r.language_label])).entries()], [rows]);
  const topics = useMemo(() => [...new Set((rows ?? []).map((r) => r.topic))].sort().map((t) => [t, t] as [string, string]), [rows]);

  return (
    <div className="space-y-6" data-testid="admin-exercises">
      <AdminHeading kicker="Exercises" title="Code exercises">
        Solved means a learner passed every test at least once. Code runs in the learner&apos;s browser; these numbers come from submitted results.
      </AdminHeading>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <AdminSelect label="Language" value={lang} onChange={setLang} options={langs} />
        <AdminSelect label="Topic" value={topic} onChange={setTopic} options={topics} />
        <AdminSelect label="Level" value={level} onChange={setLevel} options={[["beginner", "Beginner"], ["intermediate", "Intermediate"], ["advanced", "Advanced"]]} />
        <AdminSelect label="Sort" value={sort} all={null} onChange={setSort} options={[["runs", "Most runs"], ["hard", "Least solved"], ["solve_rate", "Most solved"]]} />
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      {rows && (
        <div className="card">
          <div className="hidden grid-cols-[minmax(0,1fr)_8rem_3.5rem_4.5rem_5rem_7.5rem_7.5rem] gap-4 border-b border-ink-700 px-4 py-2 lg:grid">
            {["Exercise", "Topic", "Level", "Runs", "Learners", "Solved", "Runs passing"].map((h) => <span key={h} className="label">{h}</span>)}
          </div>
          <ul>
            {shown.map((x) => (
              <li key={x.slug} className="grid grid-cols-1 gap-y-1.5 border-b border-ink-800 px-4 py-3 last:border-0 lg:grid-cols-[minmax(0,1fr)_8rem_3.5rem_4.5rem_5rem_7.5rem_7.5rem] lg:items-center lg:gap-4">
                <span className="min-w-0">
                  <span className="block truncate text-[14px] text-ink-50">{x.title}</span>
                  <span className="block truncate font-mono text-[11px] text-ink-500">{x.language_label} · {x.slug}</span>
                </span>
                <span className="truncate font-mono text-[11px] text-ink-400">{x.topic}</span>
                <span className="flex flex-wrap items-center gap-x-4 gap-y-1 lg:contents">
                  <Pips level={x.difficulty} />
                  <span className="font-mono text-[12px] text-ink-300">{num(x.runs)}<span className="lg:hidden text-ink-500"> runs</span></span>
                  <span className="font-mono text-[12px] text-ink-300">{num(x.learners)}<span className="lg:hidden text-ink-500"> learners</span></span>
                  <RateBar value={x.solve_rate} />
                  <RateBar value={x.run_pass_rate} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
