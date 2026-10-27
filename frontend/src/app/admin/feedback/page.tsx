"use client";

import { useCallback, useEffect, useState } from "react";
import { AdminHeading, Notice, Pager } from "@/components/admin/AdminShell";
import { AdminSelect } from "@/components/admin/Field";
import { adminApi, type FeedbackOut, type FeedbackRow } from "@/lib/adminApi";
import { ago } from "@/lib/when";

type F = { status: string; category: string; rating: string; q: string; page: number };

function Stars({ n }: { n: number }) {
  return (
    <span className="inline-flex gap-0.5" aria-label={`${n} out of 5`}>
      {[1, 2, 3, 4, 5].map((i) => <i key={i} className={`inline-block h-2.5 w-2.5 ${i <= n ? (n <= 2 ? "bg-signal" : "bg-accent") : "bg-ink-700"}`} />)}
    </span>
  );
}

export default function AdminFeedback() {
  const [f, setF] = useState<F | null>(null);
  const [text, setText] = useState("");
  const [data, setData] = useState<FeedbackOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    setF({ status: p.get("status") ?? "", category: p.get("category") ?? "", rating: p.get("rating") ?? "", q: "", page: 1 });
  }, []);
  useEffect(() => {
    const t = setTimeout(() => setF((x) => (x && x.q !== text ? { ...x, q: text, page: 1 } : x)), 250);
    return () => clearTimeout(t);
  }, [text]);

  const load = useCallback(() => {
    if (!f) return;
    adminApi.feedback(f).then(setData).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load feedback."));
  }, [f]);
  useEffect(load, [load]);

  const act = async (fn: () => Promise<unknown>) => {
    setError(null);
    try {
      await fn();
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "That didn't work.");
    }
  };
  const set = (k: keyof F) => (v: string) => setF((x) => (x ? { ...x, [k]: v, page: 1 } : x));
  if (!f) return null;

  return (
    <div className="space-y-6" data-testid="admin-feedback">
      <AdminHeading kicker="Feedback" title="What learners told us">
        Hidden entries stay here but leave the public wall on the feedback page. Deleting removes the entry for good.
      </AdminHeading>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <div className="col-span-2 md:col-span-1">
          <label className="flex min-w-0 flex-col gap-1">
            <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">Search</span>
            <input className="input py-1.5" type="search" value={text} onChange={(e) => setText(e.target.value)} placeholder="Words in the message" />
          </label>
        </div>
        <AdminSelect label="Status" value={f.status} onChange={set("status")} options={[["new", "Not reviewed"], ["reviewed", "Reviewed"], ["hidden", "Hidden from wall"]]} />
        <AdminSelect label="Category" value={f.category} onChange={set("category")} options={(data?.categories ?? []).map((c) => [c, c.replace(/_/g, " ")])} />
        <AdminSelect label="Rating" value={f.rating} onChange={set("rating")} options={[5, 4, 3, 2, 1].map((n) => [String(n), `${n} of 5`])} />
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      {data && (
        <>
          {data.items.length === 0 && <p className="text-[14px] text-ink-400">No feedback matches.</p>}
          <ul className="space-y-3">
            {data.items.map((x: FeedbackRow) => (
              <li key={x.id} className={`card relative ${x.hidden ? "opacity-70" : ""}`} data-testid="feedback-row">
                {!x.reviewed_at && <span className="absolute inset-y-0 left-0 w-[3px] bg-accent" aria-hidden="true" />}
                <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-ink-800 px-4 py-2.5">
                  <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
                    <Stars n={x.rating} />
                    <span className="chip px-1.5 text-[10px]">{x.category.replace(/_/g, " ")}</span>
                    {!x.reviewed_at && <span className="chip border-accent px-1.5 text-[10px] text-accent">New</span>}
                    {x.hidden && <span className="chip border-signal px-1.5 text-[10px] text-signal-soft">Off the wall</span>}
                  </div>
                  <span className="font-mono text-[11px] text-ink-500">
                    {x.author.name}{x.author.handle ? ` · @${x.author.handle}` : ""} · {ago(x.created_at)}
                  </span>
                </div>
                <div className="space-y-3 px-4 py-3">
                  <p className="whitespace-pre-line break-words text-[14px] leading-relaxed text-ink-100">{x.message}</p>
                  {x.page_context && <p className="truncate font-mono text-[11px] text-ink-500">from {x.page_context}</p>}
                  <div className="flex flex-wrap gap-1.5">
                    <button type="button" className="btn-ghost px-2 py-1 text-[11px]" onClick={() => act(() => adminApi.reviewFeedback(x.id, !x.reviewed_at))} data-testid="feedback-review">
                      {x.reviewed_at ? "Mark as new" : "Mark reviewed"}
                    </button>
                    <button type="button" className="btn-ghost px-2 py-1 text-[11px]" onClick={() => act(() => adminApi.hideFeedback(x.id, !x.hidden))} data-testid="feedback-hide">
                      {x.hidden ? "Show on wall" : "Hide from wall"}
                    </button>
                    {confirmDelete === x.id ? (
                      <span className="flex flex-wrap items-center gap-1.5">
                        <span className="text-[12px] text-signal-soft">Delete for good?</span>
                        <button type="button" className="btn-ghost border-signal px-2 py-1 text-[11px] text-signal" onClick={() => { setConfirmDelete(null); act(() => adminApi.deleteFeedback(x.id)); }}>Yes, delete</button>
                        <button type="button" className="btn-ghost px-2 py-1 text-[11px]" onClick={() => setConfirmDelete(null)}>Keep</button>
                      </span>
                    ) : (
                      <button type="button" className="btn-ghost border-signal/60 px-2 py-1 text-[11px] text-signal-soft hover:border-signal hover:text-signal" onClick={() => setConfirmDelete(x.id)}>Delete</button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <Pager page={data.page} pages={data.pages} total={data.total} onPage={(p) => setF((x) => (x ? { ...x, page: p } : x))} noun="entries" />
        </>
      )}
    </div>
  );
}
