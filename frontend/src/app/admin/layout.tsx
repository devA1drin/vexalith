import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { auth } from "@/auth";
import { backendUrl, mintBackendToken } from "@/lib/backend";
import { AdminShell } from "@/components/admin/AdminShell";

export const metadata: Metadata = { title: "Admin", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Access = { ok: true; name: string; identity: string } | { ok: false; reason: "denied" | "error" };

/** Ask the API: the backend alone decides who is an admin (ADMIN_IDENTITIES). */
async function access(): Promise<Access | null> {
  const session = await auth();
  if (!session?.user) return null;
  try {
    const res = await fetch(`${backendUrl()}/api/admin/me`, {
      headers: { Authorization: `Bearer ${await mintBackendToken(session)}`, Accept: "application/json" },
      cache: "no-store",
    });
    if (res.ok) {
      const me = await res.json();
      return { ok: true, name: String(me.name ?? ""), identity: String(me.identity ?? "") };
    }
    return { ok: false, reason: res.status === 403 || res.status === 401 ? "denied" : "error" };
  } catch {
    return { ok: false, reason: "error" };
  }
}

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const a = await access();
  if (a === null) redirect("/login?callbackUrl=/admin");
  if (!a.ok) return <Blocked reason={a.reason} />;
  return <AdminShell name={a.name} identity={a.identity}>{children}</AdminShell>;
}

function Blocked({ reason }: { reason: "denied" | "error" }) {
  const denied = reason === "denied";
  return (
    <section className="mx-auto max-w-2xl py-10" data-testid="admin-blocked">
      <div className="border border-ink-700 bg-ink-900">
        <div className="flex items-center gap-3 border-b border-ink-700 px-5 py-3">
          <span className="h-2 w-2 bg-signal" aria-hidden="true" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-signal">{denied ? "Error 403 · No access" : "Couldn't check access"}</span>
        </div>
        <div className="space-y-4 px-5 py-8 sm:px-8">
          <p className="font-display text-[56px] leading-none text-ink-50 sm:text-[72px]">{denied ? "403" : "···"}</p>
          <h1 className="font-display text-2xl text-ink-50">{denied ? "This page is for admins only." : "We couldn't confirm you're an admin."}</h1>
          <p className="max-w-md text-[15px] leading-relaxed text-ink-300">
            {denied
              ? "Your account can't open it. If you run this Vexalith and should have access, add your account to the admin list on the server."
              : "The server didn't answer. Try again in a moment."}
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href="/practice" className="btn-primary">Back to practice <span className="btn-arrow">→</span></Link>
            <Link href="/" className="btn-ghost">Home</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
