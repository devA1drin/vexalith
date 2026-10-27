"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { CodeBlock } from "@/components/CodeBlock";
import { Notice } from "@/components/admin/AdminShell";
import { RateBar } from "@/components/admin/Charts";
import { Pips } from "@/components/admin/Field";
import { HouseStyle } from "@/components/admin/HouseStyle";
import { adminApi, type QuestionDetail } from "@/lib/adminApi";
import { num, ratingBand } from "@/lib/adminFormat";
import { shortDate } from "@/lib/when";

type Draft = { question_text: string; reference_answer: string; key_idea: string };

export default function AdminQuestionEdit({ params }: { params: Promise<{ id: string }> }) {
  const id = Number(use(params).id);
  const [q, setQ] = useState<QuestionDetail | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [notes, setNotes] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    adminApi.question(id).then((d) => {
      setQ(d);
      setDraft({ question_text: d.question_text, reference_answer: d.reference_answer, key_idea: d.key_idea });
    }).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load this question."));
  }, [id]);

  useEffect(() => {
    if (!draft) return;
    const t = setTimeout(() => {
      adminApi.styleCheck(draft).then((r) => setNotes(r.notes)).catch(() => undefined);
    }, 450);
    return () => clearTimeout(t);
  }, [draft, id]);

  if (error && !q) return <Notice tone="error">{error}</Notice>;
  if (!q || !draft) return <p className="font-mono text-[12px] text-ink-500">Loading…</p>;

  const dirty = draft.question_text !== q.question_text || draft.reference_answer !== q.reference_answer || draft.key_idea !== q.key_idea;
  const set = (k: keyof Draft) => (e: React.ChangeEvent<HTMLTextAreaElement>) => { setSaved(null); setDraft({ ...draft, [k]: e.target.value }); };

  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await adminApi.saveQuestion(id, draft);
      if (r.question) {
        setQ(r.question);
        setDraft({ question_text: r.question.question_text, reference_answer: r.question.reference_answer, key_idea: r.question.key_idea });
      }
      setNotes(r.notes);
      setSaved(r.saved ? "Saved. Learners see the new text from their next question." : "Nothing changed.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't save.");
    } finally {
      setBusy(false);
    }
  };

  const toggleHidden = async () => {
    setError(null);
    try {
      const d = await adminApi.setQuestionHidden(id, !q.hidden);
      setQ({ ...q, hidden: d.hidden });
      setSaved(d.hidden ? "Hidden. Practice, quizzes, paths and the daily challenge skip it." : "Live again.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't change that.");
    }
  };

  const stats: [string, React.ReactNode][] = [
    ["Attempts", num(q.attempts ?? 0)],
    ["Learners", num(q.learners ?? 0)],
    ["Pass rate", <RateBar key="p" value={q.pass_rate} />],
    ["Missed", <RateBar key="f" value={q.fail_rate} tone="fail" />],
    ["Rating", <span key="r" className="font-mono text-[13px] text-ink-100">◆ {q.rating} <span className="text-ink-500">{ratingBand(q.rating ?? 0)}</span></span>],
  ];

  return (
    <div className="space-y-6" data-testid="admin-question-edit">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link href="/admin/questions" className="font-mono text-[12px] uppercase tracking-wider text-ink-400 hover:text-accent">← All questions</Link>
        <div className="flex flex-wrap items-center gap-2">
          {q.edited && <span className="chip border-accent/60 text-accent">Edited {q.edited_at ? shortDate(q.edited_at) : ""}</span>}
          <span className={`chip ${q.hidden ? "border-signal text-signal-soft" : "border-accent text-accent"}`}>{q.hidden ? "Hidden" : "Live"}</span>
          <button type="button" className="btn-ghost" onClick={toggleHidden} data-testid="question-hide">{q.hidden ? "Unhide" : "Hide from learners"}</button>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[12px] text-ink-400">
          <span className="text-ink-500">#{q.id}</span>
          <span>{q.topic_label}</span><span className="text-ink-700">/</span>
          <span>{q.language_label}</span><span className="text-ink-700">/</span>
          <Pips level={q.difficulty} /><span className="capitalize">{q.difficulty}</span>
          {q.kind === "fill_blank" && <><span className="text-ink-700">/</span><span>Fill in the code</span></>}
        </div>
        <h1 className="font-display text-3xl leading-tight text-ink-50">{q.title}</h1>
      </div>

      <dl className="grid grid-cols-2 border-l border-t border-ink-700 sm:grid-cols-5">
        {stats.map(([k, v]) => (
          <div key={k} className="min-w-0 border-b border-r border-ink-700 bg-ink-900 px-3 py-3">
            <dt className="label">{k}</dt>
            <dd className="mt-1.5 font-mono text-[15px] text-ink-50">{v}</dd>
          </div>
        ))}
      </dl>

      {saved && <Notice tone="ok">{saved}</Notice>}
      {error && <Notice tone="error">{error}</Notice>}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="min-w-0 space-y-5">
          {q.code && <CodeBlock code={q.code} language={q.language} />}

          <label className="block space-y-1.5">
            <span className="label">Question</span>
            <textarea className="input min-h-[5.5rem] text-[15px] leading-relaxed" value={draft.question_text} onChange={set("question_text")} data-testid="edit-question" />
            <span className="block border-l-2 border-ink-700 pl-3 text-[13px] text-ink-400">
              <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">Added under it: </span>{q.task_line}
            </span>
          </label>

          <label className="block space-y-1.5">
            <span className="label">Explanation learners see</span>
            <textarea className="input min-h-[7rem] text-[14px] leading-relaxed" value={draft.key_idea} onChange={set("key_idea")} data-testid="edit-key-idea" />
            <span className="block text-[12px] text-ink-500">Shown as the &ldquo;Key idea&rdquo; hint and in review. The general idea, not this question&apos;s answer.</span>
          </label>

          <label className="block space-y-1.5">
            <span className="label">Model answer</span>
            <textarea className="input min-h-[6rem] text-[14px] leading-relaxed" value={draft.reference_answer} onChange={set("reference_answer")} data-testid="edit-answer" />
            <span className="block text-[12px] text-ink-500">Shown after grading. Grading uses the key points below, so the score doesn&apos;t change.</span>
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button type="button" className="btn-primary" disabled={!dirty || busy} onClick={save} data-testid="question-save">{busy ? "Saving…" : "Save changes"}</button>
            {dirty && <button type="button" className="btn-ghost" onClick={() => setDraft({ question_text: q.question_text, reference_answer: q.reference_answer, key_idea: q.key_idea })}>Undo edits</button>}
          </div>
        </div>

        <div className="min-w-0 space-y-4">
          <HouseStyle notes={notes} />
          <div className="panel space-y-3 p-4">
            <div className="label">Key points graded</div>
            <ul className="space-y-1.5 text-[13px] text-ink-300">
              {q.key_points.map((k) => <li key={k} className="flex gap-2"><span className="text-accent">+</span>{k}</li>)}
            </ul>
            {q.accepted_answers.length > 0 && (
              <p className="font-mono text-[12px] text-ink-400">Accepted: {q.accepted_answers.map((a) => <code key={a} className="mr-2 text-ink-100">{a}</code>)}</p>
            )}
          </div>
          <div className="panel space-y-2 p-4">
            <div className="label">Hints, in order</div>
            <ol className="space-y-2 text-[13px] leading-relaxed text-ink-300">
              {q.hints.map((h, i) => <li key={i} className="flex gap-2"><span className="font-mono text-ink-500">{i + 1}</span><span className="min-w-0">{h}</span></li>)}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
