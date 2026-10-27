"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import Link from "next/link";
import {
  api, ApiError, LANGUAGE_IDS,
  type AnswerLanguage, type Language, type Profile, type ProfileSummary, type ProfileUpdate, type QuizOptions, type QuizScope, type QuizStartBody, type Visibility,
} from "@/lib/api";
import { Avatar } from "@/components/Avatar";
import { LevelMark } from "@/components/BadgeMark";
import { MARK_LABELS } from "@/lib/avatar";
import { ANSWER_LANGUAGE_LABEL, ANSWER_PLACEHOLDER, LANGUAGE_LABELS, changedFields } from "@/lib/prefs";
import { setProfile } from "@/lib/profileStore";

type Form = {
  display_name: string;
  handle: string;
  visibility: Visibility;
  avatar: string;
  bio: string;
  practice_languages: Language[];
  answer_language: AnswerLanguage;
  quiz_defaults: QuizStartBody | null;
};

const VISIBILITY: { v: Visibility; title: string }[] = [
  { v: "handle", title: "My handle" },
  { v: "name", title: "My name" },
  { v: "anonymous", title: "Anonymous learner" },
  { v: "hidden", title: "Hide me" },
];
const SCOPE_LABEL: Record<QuizScope, string> = { language: "Language", topic: "Topic", path: "Path", mixed: "Mixed" };

function formOf(p: Profile): Form {
  return {
    display_name: p.display_name,
    handle: p.handle,
    visibility: p.visibility,
    avatar: p.avatar,
    bio: p.bio,
    practice_languages: p.practice_languages,
    answer_language: p.answer_language,
    quiz_defaults: p.quiz_defaults,
  };
}

export default function ProfilePage() {
  const [profile, setP] = useState<Profile | null>(null);
  const [summary, setSummary] = useState<ProfileSummary | null>(null);
  const [quiz, setQuiz] = useState<QuizOptions | null>(null);
  const [form, setForm] = useState<Form | null>(null);
  const [errors, setErrors] = useState<Partial<Record<keyof Form | "form", string>>>({});
  const [handleNote, setHandleNote] = useState<{ ok: boolean; text: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    Promise.all([api.profile(), api.profileSummary(), api.quizOptions().catch(() => null)]).then(([p, s, q]) => {
      setP(p);
      setForm(formOf(p));
      setSummary(s);
      setQuiz(q);
    }).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/profile";
      else setErrors({ form: e instanceof Error ? e.message : "Couldn't load your profile." });
    });
  }, []);

  const diff = useMemo(() => (profile && form ? changedFields(formOf(profile), form) : {}), [profile, form]);
  const dirty = Object.keys(diff).length > 0;

  // Check the handle as the learner types (saving checks again).
  useEffect(() => {
    if (!profile || !form || form.handle.trim() === profile.handle) { setHandleNote(null); return; }
    const t = setTimeout(() => {
      api.checkHandle(form.handle).then((r) => setHandleNote({ ok: r.available, text: r.available ? "Available" : r.reason })).catch(() => {});
    }, 350);
    return () => clearTimeout(t);
  }, [form, profile]);

  const set = <K extends keyof Form>(k: K, v: Form[K]) => {
    setForm((f) => (f ? { ...f, [k]: v } : f));
    setErrors((e) => ({ ...e, [k]: undefined, form: undefined }));
    setSaved(false);
  };

  const save = async () => {
    if (!dirty) return;
    setSaving(true);
    setErrors({});
    try {
      const p = await api.saveProfile(diff as ProfileUpdate);
      setP(p);
      setForm(formOf(p));
      setProfile(p);
      setSaved(true);
      setHandleNote(null);
      // The first preferred language becomes the one practice opens with.
      if (diff.practice_languages && p.practice_languages[0]) localStorage.setItem("vexalith_language", p.practice_languages[0]);
    } catch (e) {
      const field = e instanceof ApiError && e.field ? (e.field as keyof Form) : "form";
      setErrors({ [field]: e instanceof Error ? e.message : "Couldn't save." });
    } finally {
      setSaving(false);
    }
  };

  if (!profile || !form) {
    return (
      <div className="space-y-6">
        {errors.form ? <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{errors.form}</p> : <div className="card h-72 animate-pulse" />}
      </div>
    );
  }

  const name = form.display_name.trim() || profile.sign_in_name || "Learner";
  const marks = profile.photo_url ? [...profile.avatars, "photo"] : profile.avatars;
  return (
    <div className="space-y-8 pb-24">
      <div className="flex flex-wrap items-end gap-5 border-b border-ink-700 pb-5">
        <Avatar mark={form.avatar} name={name} photoUrl={profile.photo_url} size={72} className="border border-ink-700" />
        <div className="min-w-0 flex-1">
          <p className="label mb-2">Profile</p>
          <h1 className="break-words font-display text-4xl font-bold tracking-tight text-ink-50" data-testid="profile-name">{name}</h1>
          <p className="mt-1 font-mono text-[12px] text-ink-400">
            {profile.visibility === "hidden" ? "Off the leaderboard" : `Ranks as ${profile.leaderboard_name}`}
            {summary?.joined_at && <> · joined {new Date(summary.joined_at).toLocaleDateString("en-US", { month: "short", year: "numeric" })}</>}
          </p>
        </div>
      </div>

      {summary && <Summary s={summary} />}

      <section className="card divide-y divide-ink-800" data-testid="profile-form">
        <Step n="01" title="How you appear" id="appearance">
          <div className="space-y-5">
            <fieldset className="min-w-0">
              <legend className="label mb-2">Mark</legend>
              <div className="grid grid-cols-6 gap-2 sm:grid-cols-11" role="radiogroup" aria-label="Mark">
                {marks.map((m) => (
                  <button
                    key={m}
                    type="button"
                    role="radio"
                    aria-checked={form.avatar === m}
                    aria-label={MARK_LABELS[m] ?? m}
                    title={MARK_LABELS[m] ?? m}
                    onClick={() => set("avatar", m)}
                    className={`grid aspect-square place-items-center border p-1 transition-colors ${form.avatar === m ? "border-accent bg-accent/10" : "border-ink-700 hover:border-ink-400"}`}
                    data-testid={`mark-${m}`}
                  >
                    <Avatar mark={m} name={name} photoUrl={profile.photo_url} size={36} />
                  </button>
                ))}
              </div>
              <Err msg={errors.avatar} />
            </fieldset>

            <Field label="Display name" hint={`Leave empty to use your sign-in name${profile.sign_in_name ? ` (${profile.sign_in_name})` : ""}.`} error={errors.display_name}>
              <input
                className="input"
                value={form.display_name}
                maxLength={profile.limits.name[1]}
                onChange={(e) => set("display_name", e.target.value)}
                placeholder={profile.sign_in_name || "Your name"}
                autoComplete="nickname"
                data-testid="display-name"
              />
            </Field>

            <Field label="Bio" hint={`Optional. Up to ${profile.limits.bio} characters, plain text.`} error={errors.bio} count={`${form.bio.length}/${profile.limits.bio}`}>
              <textarea
                className="input min-h-[5rem] text-[14px] leading-6"
                rows={3}
                value={form.bio}
                maxLength={profile.limits.bio}
                onChange={(e) => set("bio", e.target.value)}
                placeholder="What you're learning, or why."
                data-testid="bio"
              />
            </Field>
          </div>
        </Step>

        <Step n="02" title="Leaderboard" id="leaderboard">
          <div className="space-y-5">
            <Field
              label="Handle"
              hint={`${profile.limits.handle[0]} to ${profile.limits.handle[1]} letters, numbers, spaces, dots, dashes or underscores. Must be unique.`}
              error={errors.handle}
              note={handleNote && !errors.handle ? <span className={handleNote.ok ? "text-accent" : "text-signal-soft"} data-testid="handle-note">{handleNote.text}</span> : null}
            >
              <input
                className="input"
                value={form.handle}
                maxLength={profile.limits.handle[1]}
                onChange={(e) => set("handle", e.target.value)}
                autoComplete="off"
                spellCheck={false}
                data-testid="handle"
              />
            </Field>
            <fieldset className="min-w-0">
              <legend className="label mb-2">Show me as</legend>
              <div className="grid gap-2 sm:grid-cols-2">
                {VISIBILITY.map((o) => (
                  <label
                    key={o.v}
                    className={`flex cursor-pointer items-start gap-3 border p-3 transition-colors ${form.visibility === o.v ? "border-accent bg-accent/5" : "border-ink-700 hover:border-ink-500"}`}
                    data-testid={`visibility-${o.v}`}
                  >
                    <input type="radio" name="visibility" className="mt-1 accent-[#c8f031]" checked={form.visibility === o.v} onChange={() => set("visibility", o.v)} />
                    <span className="min-w-0">
                      <span className="block text-sm text-ink-50">{o.title}</span>
                      <span className="block break-words font-mono text-[12px] text-ink-400">
                        {o.v === "handle" ? form.handle || "—" : o.v === "name" ? name : o.v === "anonymous" ? "No name or handle" : "Leave me off the board"}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
              <Err msg={errors.visibility} />
            </fieldset>
            <p className="text-[13px] text-ink-400">Your email is never shown to anyone. Your mark shows next to your handle or name, not when anonymous.</p>
          </div>
        </Step>

        <Step n="03" title="Practice" id="practice">
          <div className="space-y-5">
            <fieldset className="min-w-0">
              <legend className="label mb-1">Languages you practise</legend>
              <p className="mb-2 text-[13px] text-ink-400">Practice opens with the first one you pick.</p>
              <div className="flex flex-wrap gap-2">
                {LANGUAGE_IDS.map((l) => {
                  const i = form.practice_languages.indexOf(l);
                  return (
                    <button
                      key={l}
                      type="button"
                      aria-pressed={i >= 0}
                      onClick={() => set("practice_languages", i >= 0 ? form.practice_languages.filter((x) => x !== l) : [...form.practice_languages, l])}
                      className={`inline-flex items-center gap-1.5 border px-2.5 py-1 font-mono text-[12px] transition-colors ${i >= 0 ? "border-accent text-accent" : "border-ink-700 text-ink-300 hover:border-ink-400"}`}
                      data-testid={`lang-${l}`}
                    >
                      {i === 0 && <span className="bg-accent px-1 text-[10px] text-ink-950">1st</span>}
                      {LANGUAGE_LABELS[l]}
                    </button>
                  );
                })}
              </div>
              <Err msg={errors.practice_languages} />
            </fieldset>
            <fieldset className="min-w-0">
              <legend className="label mb-1">Answer language</legend>
              <p className="mb-2 text-[13px] text-ink-400">Sets the hints in the answer box. You can still answer in any of the three.</p>
              <div className="grid grid-cols-3 border border-ink-700" role="radiogroup" aria-label="Answer language">
                {(Object.keys(ANSWER_LANGUAGE_LABEL) as AnswerLanguage[]).map((l) => (
                  <button
                    key={l}
                    type="button"
                    role="radio"
                    aria-checked={form.answer_language === l}
                    onClick={() => set("answer_language", l)}
                    className={`px-2 py-2 font-mono text-[12px] uppercase tracking-wider ${form.answer_language === l ? "bg-accent text-ink-950" : "text-ink-300 hover:text-ink-50"}`}
                    data-testid={`answer-${l}`}
                  >
                    {ANSWER_LANGUAGE_LABEL[l]}
                  </button>
                ))}
              </div>
              <p className="mt-2 border-l-2 border-ink-700 pl-3 font-mono text-[12px] text-ink-500" lang={form.answer_language === "en" ? "en" : "fil"}>
                {ANSWER_PLACEHOLDER[form.answer_language].long}
              </p>
            </fieldset>
          </div>
        </Step>

        <Step n="04" title="Quiz defaults" id="quiz">
          <QuizDefaults value={form.quiz_defaults} opts={quiz} onChange={(v) => set("quiz_defaults", v)} />
          <Err msg={errors.quiz_defaults} />
        </Step>
      </section>

      <div className="sticky bottom-0 z-30 -mx-4 flex flex-wrap items-center gap-3 border-t border-ink-700 bg-ink-950/95 px-4 py-3 sm:mx-0 sm:border sm:px-5" data-testid="save-bar">
        <button type="button" className="btn-primary" onClick={save} disabled={!dirty || saving} data-testid="save-profile">
          {saving ? "Saving…" : <>Save changes <span className="btn-arrow">→</span></>}
        </button>
        {dirty && !saving && (
          <button type="button" className="btn-ghost" onClick={() => { setForm(formOf(profile)); setErrors({}); }}>
            Undo
          </button>
        )}
        <span className="min-w-0 font-mono text-[12px]" role="status">
          {errors.form ? <span className="text-signal-soft">{errors.form}</span>
            : Object.values(errors).some(Boolean) ? <span className="text-signal-soft">Fix the highlighted field.</span>
            : saved ? <span className="text-accent">Saved.</span>
            : dirty ? <span className="text-ink-400">Unsaved changes</span> : null}
        </span>
      </div>
    </div>
  );
}

function Summary({ s }: { s: ProfileSummary }) {
  const cells = [
    { n: s.xp.toLocaleString(), label: "XP" },
    { n: `${s.badges_earned}/${s.badges_total}`, label: "Badges", href: "/badges" },
    { n: `${s.paths_finished}/${s.paths.length}`, label: "Paths finished", href: "/paths" },
    { n: s.bookmarks, label: "Bookmarks", href: "/bookmarks" },
  ];
  const started = s.paths.filter((p) => p.started || p.steps_done > 0);
  return (
    <section className="space-y-3" data-testid="profile-summary" aria-label="Your numbers">
      <div className="grid grid-cols-2 gap-px border border-ink-700 bg-ink-700 md:grid-cols-5">
        <div className="col-span-2 flex items-center gap-3 bg-ink-950 p-4 md:col-span-1">
          <LevelMark level={s.level} size={36} />
          <div className="min-w-0">
            <div className="font-display text-2xl font-bold text-ink-50">Level {s.level}</div>
            <div className="label mt-0.5 truncate">{s.level_name}</div>
          </div>
        </div>
        {cells.map((c) => {
          const body = (
            <>
              <div className="font-display text-3xl font-bold tabular-nums text-ink-50">{c.n}</div>
              <div className="label mt-1">{c.label}</div>
            </>
          );
          return c.href ? (
            <Link key={c.label} href={c.href} className="bg-ink-950 p-4 transition-colors hover:bg-ink-900">{body}</Link>
          ) : (
            <div key={c.label} className="bg-ink-950 p-4">{body}</div>
          );
        })}
      </div>
      {started.length > 0 && (
        <ul className="grid gap-2 sm:grid-cols-2" data-testid="profile-paths">
          {started.map((p) => (
            <li key={p.slug}>
              <Link href={`/paths/${p.slug}`} className="panel flex items-center gap-3 px-3 py-2 transition-colors hover:border-ink-500">
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[14px] text-ink-100">{p.name}</span>
                  <span className="mt-1 block h-1 bg-ink-800"><span className="block h-full bg-accent" style={{ width: `${Math.round(p.progress * 100)}%` }} /></span>
                </span>
                <span className="font-mono text-[12px] text-ink-400">{p.finished ? "Done" : `${p.steps_done}/${p.steps_total}`}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function QuizDefaults({ value, opts, onChange }: { value: QuizStartBody | null; opts: QuizOptions | null; onChange: (v: QuizStartBody | null) => void }) {
  if (!opts) return <p className="text-[13px] text-ink-400">Quiz options aren&apos;t available right now.</p>;
  const scopes = (Object.keys(SCOPE_LABEL) as QuizScope[]).filter((s) => opts.scopes[s]?.length);
  const fresh = (): QuizStartBody => {
    const scope = scopes[0] ?? "mixed";
    return { scope, value: scope === "mixed" ? "" : opts.scopes[scope][0]?.value ?? "", length: opts.lengths[0], minutes: opts.minutes[0], instant: false };
  };
  const v = value;
  const patch = (p: Partial<QuizStartBody>) => v && onChange({ ...v, ...p });
  return (
    <div className="space-y-4">
      <label className="flex cursor-pointer items-center gap-3">
        <input type="checkbox" className="accent-[#c8f031]" checked={!!v} onChange={(e) => onChange(e.target.checked ? fresh() : null)} data-testid="quiz-defaults-on" />
        <span className="text-sm text-ink-100">Start new quizzes with these settings</span>
      </label>
      {v && (
        <div className="grid gap-3 sm:grid-cols-2">
          <Pick label="Scope" value={v.scope} onChange={(s) => {
            const scope = s as QuizScope;
            patch({ scope, value: scope === "mixed" ? "" : opts.scopes[scope][0]?.value ?? "" });
          }} options={scopes.map((s) => ({ value: s, label: SCOPE_LABEL[s] }))} />
          {v.scope !== "mixed" ? (
            <Pick label={SCOPE_LABEL[v.scope]} value={v.value} onChange={(x) => patch({ value: x })} options={opts.scopes[v.scope].map((o) => ({ value: o.value, label: o.label }))} />
          ) : <div className="hidden sm:block" />}
          <Pick label="Questions" value={String(v.length)} onChange={(x) => patch({ length: Number(x) })} options={opts.lengths.map((n) => ({ value: String(n), label: String(n) }))} />
          <Pick label="Time limit" value={String(v.minutes)} onChange={(x) => patch({ minutes: Number(x) })} options={opts.minutes.map((n) => ({ value: String(n), label: `${n} min` }))} />
          <Pick label="Feedback" value={v.instant ? "1" : "0"} onChange={(x) => patch({ instant: x === "1" })} options={[{ value: "0", label: "At the end" }, { value: "1", label: "After each one" }]} />
        </div>
      )}
    </div>
  );
}

function Pick({ label, value, options, onChange }: { label: string; value: string; options: { value: string; label: string }[]; onChange: (v: string) => void }) {
  return (
    <label className="flex min-w-0 flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">{label}</span>
      <select className="input w-full min-w-0 py-1.5 text-[13px]" value={value} onChange={(e) => onChange(e.target.value)} data-testid={`quiz-${label.toLowerCase().replace(/\s+/g, "-")}`}>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  );
}

function Step({ n, title, id, children }: { n: string; title: string; id: string; children: ReactNode }) {
  return (
    <div id={id} className="scroll-mt-24 p-4 sm:p-5">
      <h2 className="mb-4 flex items-baseline gap-3 font-display text-lg font-semibold text-ink-50">
        <span className="font-mono text-[12px] text-accent">{n}</span>{title}
      </h2>
      {children}
    </div>
  );
}

function Field({ label, hint, error, note, count, children }: { label: string; hint?: string; error?: string; note?: ReactNode; count?: string; children: ReactNode }) {
  return (
    <label className={`block min-w-0 ${error ? "[&_.input]:border-signal" : ""}`}>
      <span className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
        <span className="label">{label}</span>
        {count && <span className="font-mono text-[11px] text-ink-500">{count}</span>}
      </span>
      {children}
      <span className="mt-1 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 text-[12px]">
        <span className="text-ink-500">{hint}</span>
        {note && <span className="font-mono">{note}</span>}
      </span>
      <Err msg={error} />
    </label>
  );
}

function Err({ msg }: { msg?: string }) {
  if (!msg) return null;
  return <span role="alert" className="mt-1 block font-mono text-[12px] text-signal-soft" data-testid="field-error">{msg}</span>;
}
