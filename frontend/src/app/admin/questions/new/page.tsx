"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AdminHeading, Notice } from "@/components/admin/AdminShell";
import { AdminSelect } from "@/components/admin/Field";
import { HouseStyle } from "@/components/admin/HouseStyle";
import { adminApi, type NewQuestion, type QuestionsOut } from "@/lib/adminApi";

const START: NewQuestion = {
  topic: "", language: "python", difficulty: "beginner", title: "", code: "",
  question_text: "", key_points: "", reference_answer: "", key_idea: "",
};

export default function AdminNewQuestion() {
  const router = useRouter();
  const [f, setF] = useState<NewQuestion>(START);
  const [meta, setMeta] = useState<QuestionsOut | null>(null);
  const [notes, setNotes] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    adminApi.questions({ page: 1 }).then((d) => { setMeta(d); setF((x) => ({ ...x, topic: x.topic || d.topics[0]?.slug || "" })); }).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!f.question_text && !f.key_idea) return;
    const t = setTimeout(() => {
      adminApi.styleCheck({ question_text: f.question_text, key_idea: f.key_idea || undefined, reference_answer: f.reference_answer || undefined })
        .then((r) => setNotes(r.notes)).catch(() => undefined);
    }, 500);
    return () => clearTimeout(t);
  }, [f]);

  const set = (k: keyof NewQuestion) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setF({ ...f, [k]: e.target.value });
  const ready = f.topic && f.title.trim().length >= 3 && f.question_text.trim().length >= 10 && f.key_points.trim() && f.reference_answer.trim().length >= 10;

  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await adminApi.createQuestion(f);
      if (r.question) router.push(`/admin/questions/${r.question.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't add it.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="admin-new-question">
      <Link href="/admin/questions" className="font-mono text-[12px] uppercase tracking-wider text-ink-400 hover:text-accent">← All questions</Link>
      <AdminHeading kicker="New question" title="Add a question">
        It goes into Practice and recommendations straight away. Quizzes, paths and the daily challenge stay on the built-in bank. The line telling learners how to answer, and the first and last hints, are written for you.
      </AdminHeading>
      {error && <Notice tone="error">{error}</Notice>}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="min-w-0 space-y-5">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <AdminSelect label="Topic" value={f.topic} all={null} onChange={(v) => setF({ ...f, topic: v })} options={(meta?.topics ?? []).map((t) => [t.slug, t.name])} />
            <AdminSelect label="Language" value={f.language} all={null} onChange={(v) => setF({ ...f, language: v })} options={(meta?.languages ?? []).map((l) => [l.key, l.label])} />
            <AdminSelect label="Level" value={f.difficulty} all={null} onChange={(v) => setF({ ...f, difficulty: v })} options={[["beginner", "Beginner"], ["intermediate", "Intermediate"], ["advanced", "Advanced"]]} />
          </div>
          <label className="block space-y-1.5"><span className="label">Title</span><input className="input" value={f.title} onChange={set("title")} maxLength={120} /></label>
          <label className="block space-y-1.5"><span className="label">Code (optional)</span><textarea className="input min-h-[7rem] font-mono text-[13px]" value={f.code} onChange={set("code")} spellCheck={false} /></label>
          <label className="block space-y-1.5"><span className="label">Question</span><textarea className="input min-h-[5rem] text-[15px]" value={f.question_text} onChange={set("question_text")} placeholder="What does this print when the list is empty?" /></label>
          <label className="block space-y-1.5">
            <span className="label">Key points a good answer mentions</span>
            <textarea className="input min-h-[5rem] text-[14px]" value={f.key_points} onChange={set("key_points")} placeholder={"One per line. Add words to look for after a dash:\nThe loop never runs — never runs, skipped, empty"} />
          </label>
          <label className="block space-y-1.5"><span className="label">Model answer</span><textarea className="input min-h-[5rem] text-[14px]" value={f.reference_answer} onChange={set("reference_answer")} /></label>
          <label className="block space-y-1.5"><span className="label">Explanation learners see</span><textarea className="input min-h-[5rem] text-[14px]" value={f.key_idea} onChange={set("key_idea")} placeholder="The main idea, a strategy that carries over, the usual mistake." /></label>
          <button type="button" className="btn-primary" disabled={!ready || busy} onClick={save}>{busy ? "Adding…" : "Add question"}</button>
        </div>
        <div className="min-w-0"><HouseStyle notes={notes} /></div>
      </div>
    </div>
  );
}
