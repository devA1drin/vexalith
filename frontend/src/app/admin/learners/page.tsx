"use client";

import { useCallback, useEffect, useState } from "react";
import { Avatar } from "@/components/Avatar";
import { AdminHeading, Notice, Pager } from "@/components/admin/AdminShell";
import { ConfirmDialog } from "@/components/admin/ConfirmDialog";
import { adminApi, type Learner, type LearnersOut } from "@/lib/adminApi";
import { num } from "@/lib/adminFormat";
import { ago, shortDate } from "@/lib/when";

const SORTS = [
  ["recent", "Last active"],
  ["xp", "Most XP"],
  ["attempts", "Most attempts"],
  ["joined", "Newest"],
  ["name", "Name"],
] as const;

type Pending = { kind: "reset" | "delete"; learner: Learner } | null;

export default function AdminLearners() {
  const [q, setQ] = useState("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("recent");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<LearnersOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [pending, setPending] = useState<Pending>(null);
  const [busy, setBusy] = useState(false);
  const [dialogError, setDialogError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => { setQuery(q); setPage(1); }, 250);
    return () => clearTimeout(t);
  }, [q]);

  const load = useCallback(() => {
    adminApi.learners({ q: query, sort, page }).then(setData).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load learners."));
  }, [query, sort, page]);
  useEffect(load, [load]);

  const patch = (l: Learner) => setData((d) => (d ? { ...d, items: d.items.map((x) => (x.id === l.id ? l : x)) } : d));

  const toggleBoard = async (l: Learner) => {
    setError(null);
    try {
      patch(await adminApi.setBoard(l.id, !l.board_hidden));
      setNote(l.board_hidden ? `${l.name} is back on the leaderboard.` : `${l.name} is hidden from the leaderboard.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't change that.");
    }
  };

  const confirm = async (typed: string) => {
    if (!pending) return;
    setBusy(true);
    setDialogError(null);
    try {
      if (pending.kind === "reset") {
        patch(await adminApi.resetXp(pending.learner.id, typed));
        setNote(`${pending.learner.name}'s XP is now 0.`);
      } else {
        await adminApi.deleteLearner(pending.learner.id, typed);
        setNote(`${pending.learner.name}'s account and data were deleted.`);
        load();
      }
      setPending(null);
    } catch (e) {
      setDialogError(e instanceof Error ? e.message : "That didn't work.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="admin-learners">
      <AdminHeading kicker="Learners" title="Everyone who has signed in">
        Emails show only here. Search by name, handle, email or sign-in identity.
      </AdminHeading>

      <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_12rem]">
        <label className="flex min-w-0 flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">Search</span>
          <input className="input" type="search" placeholder="Name, @handle, email…" value={q} onChange={(e) => setQ(e.target.value)} data-testid="learner-search" />
        </label>
        <label className="flex min-w-0 flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">Sort</span>
          <select className="input py-2 text-[13px]" value={sort} onChange={(e) => { setSort(e.target.value); setPage(1); }}>
            {SORTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>
      </div>

      {note && <Notice tone="ok">{note}</Notice>}
      {error && <Notice tone="error">{error}</Notice>}

      {data && (
        <>
          <div className="card">
            <div className="hidden grid-cols-[minmax(0,1.5fr)_minmax(0,1.2fr)_7rem_4.5rem_6rem_18.5rem] gap-4 border-b border-ink-700 px-4 py-2 lg:grid">
              {["Learner", "Email", "Level · XP", "Attempts", "Last active", ""].map((h) => <span key={h} className="label">{h}</span>)}
            </div>
            {data.items.length === 0 && <p className="px-4 py-6 text-[14px] text-ink-400">No learners match that search.</p>}
            <ul>
              {data.items.map((l) => (
                <li key={l.id} className="grid gap-x-4 gap-y-2 border-b border-ink-800 px-4 py-3 last:border-0 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1.2fr)_7rem_4.5rem_6rem_18.5rem] lg:items-center" data-testid="learner-row">
                  <div className="flex min-w-0 items-center gap-3">
                    <Avatar mark={l.avatar ?? "initials-ink"} name={l.name} size={32} />
                    <div className="min-w-0">
                      <div className="flex min-w-0 items-center gap-2">
                        <span className="truncate text-[14px] text-ink-50">{l.name}</span>
                        {l.is_admin && <span className="chip shrink-0 border-accent px-1.5 text-[10px] text-accent">Admin</span>}
                        {l.board_hidden && <span className="chip shrink-0 border-signal px-1.5 text-[10px] text-signal-soft">Off board</span>}
                      </div>
                      <div className="truncate font-mono text-[11px] text-ink-500">{l.handle ? `@${l.handle}` : "no handle yet"} · {l.provider}</div>
                    </div>
                  </div>
                  <div className="min-w-0 truncate font-mono text-[12px] text-ink-300" title={l.email ?? ""}>{l.email ?? "—"}</div>
                  <div className="flex gap-4 font-mono text-[12px] lg:contents">
                    <span className="whitespace-nowrap text-ink-200"><span className="lg:hidden text-ink-500">Level </span>L{l.level} · {num(l.xp)} XP</span>
                    <span className="text-ink-300">{num(l.attempts + l.exercise_runs)}<span className="lg:hidden text-ink-500"> attempts</span></span>
                    <span className="text-ink-300" title={l.last_active ?? ""}>{l.last_active ? ago(l.last_active) : `joined ${shortDate(l.joined)}`}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 lg:flex-nowrap lg:justify-end">
                    <button type="button" className="btn-ghost whitespace-nowrap px-2 py-1 text-[11px]" onClick={() => toggleBoard(l)} data-testid="board-toggle">
                      {l.board_hidden ? "Show on board" : "Hide from board"}
                    </button>
                    <button type="button" className="btn-ghost whitespace-nowrap px-2 py-1 text-[11px]" onClick={() => { setDialogError(null); setPending({ kind: "reset", learner: l }); }} data-testid="reset-xp">
                      Reset XP
                    </button>
                    <button type="button" className="btn-ghost whitespace-nowrap border-signal/60 px-2 py-1 text-[11px] text-signal-soft hover:border-signal hover:text-signal" onClick={() => { setDialogError(null); setPending({ kind: "delete", learner: l }); }} data-testid="delete-learner">
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <Pager page={data.page} pages={data.pages} total={data.total} onPage={setPage} noun={data.total === 1 ? "learner" : "learners"} />
        </>
      )}

      {pending && (
        <ConfirmDialog
          title={pending.kind === "delete" ? `Delete ${pending.learner.name}?` : `Reset ${pending.learner.name}'s XP?`}
          word={pending.learner.handle ? `@${pending.learner.handle}` : pending.learner.confirm_word}
          action={pending.kind === "delete" ? "Delete everything" : "Reset XP to 0"}
          busy={busy}
          error={dialogError}
          onConfirm={confirm}
          onClose={() => setPending(null)}
        >
          {pending.kind === "delete" ? (
            <>
              <p>This removes their account and everything tied to it: answers, grades, mastery, quizzes, code runs, XP and badges, paths, bookmarks, profile and settings, and their feedback.</p>
              <p className="font-mono text-[12px] text-ink-400">{num(pending.learner.attempts)} answers · {num(pending.learner.exercise_runs)} code runs · {num(pending.learner.xp)} XP</p>
              <p>If they sign in again they start from scratch.</p>
            </>
          ) : (
            <>
              <p>Their {num(pending.learner.xp)} XP goes to 0 and their level drops to 1. Answers, badges and progress stay. Work they already did won&apos;t earn XP again; new work will.</p>
            </>
          )}
        </ConfirmDialog>
      )}
    </div>
  );
}
