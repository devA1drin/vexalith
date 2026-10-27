"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type Bookmark, type BookmarkFilters, type BookmarksOut } from "@/lib/api";
import { KindTabs, Select } from "@/components/FilterControls";
import { PageIntro } from "@/components/PageIntro";
import { bookmarkHref, bookmarkQuery, readBookmarkFilters } from "@/lib/bookmarkFilters";
import { markSaved } from "@/lib/bookmarkStore";
import { ago, LEVEL } from "@/lib/when";

const PAGE = 10;

const RESULT: Record<Bookmark["result"], [string, string]> = {
  right: ["Got it right", "border-accent text-accent"],
  solved: ["Solved", "border-accent text-accent"],
  partial: ["Partly right", "border-ink-400 text-ink-200"],
  wrong: ["Missed last time", "border-signal text-signal"],
  failed: ["Not solved yet", "border-signal text-signal"],
  new: ["Not tried", "border-ink-600 text-ink-400"],
};

export default function BookmarksPage() {
  const [filters, setFilters] = useState<BookmarkFilters | null>(null);
  const [data, setData] = useState<BookmarksOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shown, setShown] = useState(PAGE);
  const [removed, setRemoved] = useState<Bookmark | null>(null);

  useEffect(() => setFilters(readBookmarkFilters(window.location.search)), []);

  const load = useCallback((f: BookmarkFilters) => {
    api.bookmarks(f).then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/bookmarks";
      else setError(e instanceof Error ? e.message : "Couldn't load your bookmarks.");
    });
  }, []);

  useEffect(() => {
    if (!filters) return;
    setShown(PAGE);
    window.history.replaceState(null, "", `/bookmarks${bookmarkQuery(filters)}`);
    load(filters);
  }, [filters, load]);

  const set = (k: keyof BookmarkFilters, v: string) => setFilters((f) => ({ ...(f ?? {}), [k]: v || undefined }));
  const active = filters ? Object.values(filters).filter(Boolean).length : 0;

  const remove = async (b: Bookmark) => {
    setError(null);
    try {
      await api.setBookmark(b.key, false);
      markSaved(b.key, false);
      setRemoved(b);
      if (filters) load(filters);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't remove it.");
    }
  };

  const undo = async () => {
    if (!removed) return;
    const b = removed;
    setRemoved(null);
    try {
      await api.setBookmark(b.key, true, b.note);
      markSaved(b.key, true);
      if (filters) load(filters);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't put it back.");
    }
  };

  const saveNote = async (b: Bookmark, note: string) => {
    const r = await api.setBookmark(b.key, true, note);
    setData((d) => d && { ...d, items: d.items.map((x) => (x.key === b.key ? { ...x, note: r.note } : x)) });
  };

  const questions = data?.items.filter((i) => i.kind === "question").length ?? 0;
  const practiceHref = `/bookmarks/practice${bookmarkQuery({ ...(filters ?? {}), kind: undefined })}`;
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">Bookmarks</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Saved for later.</h1>
        </div>
        {questions > 0 && (
          <Link href={practiceHref} className="btn-primary" data-testid="practice-bookmarks">
            Practice my bookmarks <span className="btn-arrow">→</span>
          </Link>
        )}
      </div>
      {data && data.counts.total > 0 && (
        <PageIntro>
          Questions and coding exercises you saved with the Save button. Add a short note to remember why, then practise the
          questions here with the usual grading.
        </PageIntro>
      )}

      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {removed && (
        <div role="status" className="flex flex-wrap items-center gap-3 border border-ink-600 bg-ink-900 px-4 py-2.5 text-[14px]" data-testid="removed-note">
          <span className="min-w-0 flex-1 break-words text-ink-200">Removed “{removed.title}”.</span>
          <button type="button" className="font-mono text-[12px] uppercase tracking-wider text-accent hover:underline" onClick={undo}>Undo</button>
        </div>
      )}
      {!data && !error && <div className="card h-40 animate-pulse" />}
      {data && data.counts.total === 0 && <NoneYet />}
      {data && data.counts.total > 0 && (
        <>
          <div className="panel space-y-3 p-4" data-testid="bookmark-filters">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="label">
                {data.counts.total} saved · {data.counts.questions} questions · {data.counts.exercises} code
              </span>
              <div className="flex flex-wrap items-center gap-3">
                <KindTabs value={filters?.kind ?? ""} onChange={(v) => set("kind", v)} />
                {active > 0 && (
                  <button type="button" className="font-mono text-[12px] text-ink-400 underline-offset-4 hover:text-accent hover:underline" onClick={() => setFilters({})}>
                    Clear filters
                  </button>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Select label="Topic" value={filters?.topic} options={data.filters.topics} onChange={(v) => set("topic", v)} />
              <Select label="Language" value={filters?.language} options={data.filters.languages} onChange={(v) => set("language", v)} />
            </div>
          </div>

          {data.items.length === 0 ? (
            <div className="card flex flex-col items-start gap-3 p-6" data-testid="bookmarks-empty">
              <h2 className="font-display text-2xl font-semibold text-ink-50">Nothing matches these filters.</h2>
              <button type="button" className="btn-ghost" onClick={() => setFilters({})}>Clear filters</button>
            </div>
          ) : (
            <ul className="space-y-3" data-testid="bookmark-list">
              {data.items.slice(0, shown).map((b, i) => (
                <Card key={b.key} b={b} i={i % PAGE} noteMax={data.limits.note} filters={filters ?? {}} onRemove={() => remove(b)} onNote={(n) => saveNote(b, n)} />
              ))}
            </ul>
          )}
          {data.items.length > shown && (
            <button type="button" className="btn-ghost w-full justify-center" onClick={() => setShown((n) => n + PAGE)} data-testid="show-more">
              Show {Math.min(PAGE, data.items.length - shown)} more · {data.items.length - shown} left
            </button>
          )}
        </>
      )}
    </div>
  );
}

function NoneYet() {
  return (
    <div className="card flex flex-col items-start gap-3 p-6" data-testid="bookmarks-none">
      <h2 className="font-display text-2xl font-semibold text-ink-50">No bookmarks yet.</h2>
      <p className="max-w-xl text-[14px] text-ink-300">
        Press <b className="font-mono text-[12px] uppercase tracking-wider text-ink-100">Save</b> on any question in Practice, Review, a quiz&apos;s
        results or a path step, or on a coding exercise. It shows up here.
      </p>
      <div className="flex flex-wrap gap-3">
        <Link href="/practice" className="btn-primary">Go to Practice <span className="btn-arrow">→</span></Link>
        <Link href="/code" className="btn-ghost">Browse Code</Link>
      </div>
    </div>
  );
}

function Card({ b, i, noteMax, filters, onRemove, onNote }: {
  b: Bookmark; i: number; noteMax: number; filters: BookmarkFilters; onRemove: () => void; onNote: (note: string) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [note, setNote] = useState(b.note);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [word, tone] = RESULT[b.result];
  const level = LEVEL[b.difficulty] ?? 1;

  const save = async () => {
    setBusy(true);
    setErr(null);
    try {
      await onNote(note);
      setEditing(false);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Couldn't save the note.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <li className="rise card relative overflow-hidden" style={{ ["--rd" as string]: `${Math.min(i, 8) * 35}ms` }} data-testid={`bookmark-${b.key}`}>
      <div className="flex flex-wrap items-center gap-2 border-b border-ink-800 px-4 py-2.5 sm:px-5">
        <span className={`chip ${tone}`}>{word}</span>
        <span className="chip text-ink-100">{b.kind === "exercise" ? `Code · ${b.topic_name}` : b.topic_name}</span>
        <span className="chip uppercase">{b.language === "cpp" ? "C++" : b.language}</span>
        <span className="chip gap-1.5" title={b.difficulty}>
          {[1, 2, 3].map((n) => <span key={n} className={`inline-block h-2 w-2 ${n <= level ? "bg-accent" : "bg-ink-700"}`} />)}
        </span>
        <span className="ml-auto font-mono text-[11px] text-ink-500">saved {ago(b.saved_at)}</span>
      </div>
      <div className="space-y-3 p-4 sm:p-5">
        <h3 className="break-words font-display text-lg font-semibold leading-snug text-ink-50">{b.title}</h3>
        {editing ? (
          <div className="space-y-2">
            <input
              className="input text-[14px]"
              value={note}
              maxLength={noteMax}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") save(); if (e.key === "Escape") { setNote(b.note); setEditing(false); } }}
              placeholder="e.g. tricky off-by-one, retry Friday"
              aria-label="Note"
              autoFocus
              data-testid="note-input"
            />
            <div className="flex flex-wrap items-center gap-3">
              <button type="button" className="btn-primary py-[6px]" onClick={save} disabled={busy} data-testid="note-save">{busy ? "Saving…" : "Save note"}</button>
              <button type="button" className="btn-ghost py-[6px]" onClick={() => { setNote(b.note); setEditing(false); }}>Cancel</button>
              <span className="ml-auto font-mono text-[11px] text-ink-500">{note.length}/{noteMax}</span>
            </div>
            {err && <p role="alert" className="font-mono text-[12px] text-signal-soft">{err}</p>}
          </div>
        ) : b.note ? (
          <button type="button" onClick={() => setEditing(true)} className="block w-full border-l-2 border-accent/60 pl-3 text-left text-[14px] text-ink-200 hover:text-ink-50" data-testid="note">
            {b.note}
          </button>
        ) : null}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2 pt-1">
          {b.kind === "question" ? (
            <Link href={`/bookmarks/practice${bookmarkQuery({ ...filters, kind: undefined }, { start: b.key })}`} className="btn-primary py-[7px]" data-testid="practice-one">
              Practise <span className="btn-arrow">→</span>
            </Link>
          ) : (
            <Link href={bookmarkHref(b)} className="btn-primary py-[7px]">Open exercise <span className="btn-arrow">→</span></Link>
          )}
          {b.kind === "question" && <Link href={bookmarkHref(b)} className="btn-ghost py-[7px]">Open in Practice</Link>}
          {!editing && !b.note && (
            <button type="button" className="font-mono text-[12px] text-ink-400 underline-offset-4 hover:text-accent hover:underline" onClick={() => setEditing(true)} data-testid="add-note">
              Add a note
            </button>
          )}
          <button type="button" className="ml-auto font-mono text-[12px] text-ink-500 underline-offset-4 hover:text-signal-soft hover:underline" onClick={onRemove} data-testid="remove">
            Remove
          </button>
        </div>
      </div>
    </li>
  );
}
