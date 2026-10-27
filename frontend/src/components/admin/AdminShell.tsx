"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/admin", label: "Overview" },
  { href: "/admin/learners", label: "Learners" },
  { href: "/admin/questions", label: "Questions" },
  { href: "/admin/exercises", label: "Exercises" },
  { href: "/admin/feedback", label: "Feedback" },
  { href: "/admin/audit", label: "Audit log" },
];

export function AdminShell({ name, identity, children }: { name: string; identity: string; children: React.ReactNode }) {
  const path = usePathname();
  const active = (href: string) => (href === "/admin" ? path === "/admin" : path === href || path.startsWith(`${href}/`));
  return (
    <div className="space-y-8" data-testid="admin-shell">
      <div className="border border-ink-700 bg-ink-950">
        <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-b border-ink-700 px-4 py-3 sm:px-5">
          <div className="flex min-w-0 items-center gap-3">
            <span className="inline-flex items-center gap-1.5 bg-signal px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-ink-950">
              <span className="h-1.5 w-1.5 bg-ink-950" aria-hidden="true" /> Restricted
            </span>
            <span className="font-display text-lg leading-none text-ink-50">Admin console</span>
          </div>
          <div className="min-w-0 truncate font-mono text-[11px] text-ink-500" title={identity}>
            signed in as <span className="text-ink-200">{name}</span>
          </div>
        </div>
        <nav aria-label="Admin sections" className="overflow-x-auto">
          <ul className="flex min-w-max">
            {TABS.map((t, i) => (
              <li key={t.href}>
                <Link
                  href={t.href}
                  aria-current={active(t.href) ? "page" : undefined}
                  className={`relative flex items-baseline gap-2 border-r border-ink-800 px-4 py-2.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${
                    active(t.href) ? "bg-ink-900 text-accent" : "text-ink-400 hover:bg-ink-900 hover:text-ink-100"
                  }`}
                  data-testid={`admin-tab-${t.label.split(" ")[0].toLowerCase()}`}
                >
                  {active(t.href) && <span className="absolute inset-x-0 top-0 h-[2px] bg-accent" aria-hidden="true" />}
                  <span className={active(t.href) ? "text-accent/70" : "text-ink-600"}>{String(i + 1).padStart(2, "0")}</span>
                  {t.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
      {children}
    </div>
  );
}

/** Section title used by every admin page. */
export function AdminHeading({ kicker, title, children, actions }: { kicker: string; title: string; children?: React.ReactNode; actions?: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0 space-y-2">
        <div className="label text-accent">{kicker}</div>
        <h1 className="font-display text-3xl leading-tight text-ink-50 sm:text-4xl">{title}</h1>
        {children && <p className="max-w-2xl text-[15px] leading-relaxed text-ink-300">{children}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Pager({ page, pages, total, onPage, noun }: { page: number; pages: number; total: number; onPage: (p: number) => void; noun: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 font-mono text-[12px] text-ink-400" data-testid="pager">
      <span>
        {total.toLocaleString("en-US")} {noun}
        {pages > 1 && ` · page ${page} of ${pages}`}
      </span>
      {pages > 1 && (
        <div className="flex gap-2">
          <button type="button" className="btn-ghost px-2.5 py-1" disabled={page <= 1} onClick={() => onPage(page - 1)}>← Prev</button>
          <button type="button" className="btn-ghost px-2.5 py-1" disabled={page >= pages} onClick={() => onPage(page + 1)}>Next →</button>
        </div>
      )}
    </div>
  );
}

export function Notice({ tone = "plain", children }: { tone?: "plain" | "error" | "ok"; children: React.ReactNode }) {
  const c = tone === "error" ? "border-signal text-signal-soft" : tone === "ok" ? "border-accent text-ink-100" : "border-ink-600 text-ink-200";
  return <div role="status" className={`border-l-2 bg-ink-900 px-4 py-2.5 text-[14px] ${c}`}>{children}</div>;
}
