"use client";

import { useEffect, useState } from "react";
import { AdminHeading, Notice, Pager } from "@/components/admin/AdminShell";
import { AdminSelect } from "@/components/admin/Field";
import { adminApi, type AuditOut } from "@/lib/adminApi";
import { actionLabel, actionTone } from "@/lib/adminFormat";

function detailText(d: Record<string, unknown>): string {
  const parts: string[] = [];
  if (typeof d.previous_xp === "number") parts.push(`was ${d.previous_xp.toLocaleString("en-US")} XP`);
  if (Array.isArray(d.fields)) parts.push(`changed ${d.fields.map((f) => String(f).replace(/_/g, " ")).join(", ")}`);
  if (d.removed && typeof d.removed === "object") {
    const r = d.removed as Record<string, number>;
    parts.push(Object.entries(r).map(([k, v]) => `${v} ${k.replace(/_/g, " ")}`).join(", "));
  }
  if (typeof d.excerpt === "string") parts.push(`“${d.excerpt}”`);
  return parts.join(" · ");
}

const TONE = { danger: "bg-signal", edit: "bg-accent", plain: "bg-ink-500" };

export default function AdminAudit() {
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<AuditOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    adminApi.audit({ action, page }).then(setData).catch((e) => setError(e instanceof Error ? e.message : "Couldn't load the log."));
  }, [action, page]);

  return (
    <div className="space-y-6" data-testid="admin-audit">
      <AdminHeading kicker="Audit log" title="Every admin change">
        Who did what, newest first. Entries can&apos;t be edited, and they name learners by number and handle, never by email.
      </AdminHeading>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <AdminSelect label="Action" value={action} onChange={(v) => { setAction(v); setPage(1); }} options={(data?.actions ?? []).map((a) => [a, actionLabel(a)])} />
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      {data && (
        <>
          {data.items.length === 0 ? (
            <p className="text-[14px] text-ink-400">Nothing logged yet.</p>
          ) : (
            <ol className="relative border-l border-ink-700 pl-0">
              {data.items.map((a) => {
                const when = new Date(a.created_at);
                const extra = detailText(a.details);
                return (
                  <li key={a.id} className="relative grid gap-x-5 gap-y-1 border-b border-ink-800 py-3 pl-5 pr-2 sm:grid-cols-[9.5rem_minmax(0,1fr)]" data-testid="audit-row">
                    <span className={`absolute -left-[4.5px] top-[1.15rem] h-2 w-2 ${TONE[actionTone(a.action)]}`} aria-hidden="true" />
                    <time dateTime={a.created_at} className="font-mono text-[12px] text-ink-500">
                      {when.toLocaleDateString("en-US", { month: "short", day: "numeric" })} · {when.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                    </time>
                    <div className="min-w-0 space-y-0.5">
                      <p className="text-[14px] text-ink-100">
                        <span className="text-ink-50">{a.actor}</span> <span className={actionTone(a.action) === "danger" ? "text-signal-soft" : "text-ink-300"}>{actionLabel(a.action).toLowerCase()}</span>
                        <span className="text-ink-400"> · </span><span className="break-words font-mono text-[13px] text-ink-200">{a.target}</span>
                      </p>
                      {extra && <p className="break-words text-[12px] text-ink-500">{extra}</p>}
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
          <Pager page={data.page} pages={data.pages} total={data.total} onPage={setPage} noun="entries" />
        </>
      )}
    </div>
  );
}
