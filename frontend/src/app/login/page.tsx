import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { auth, availableProviders, signIn } from "@/auth";
import { LogoMark } from "@/components/Logo";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Sign in" };

function safeCallback(raw: string | string[] | undefined): string {
  const v = Array.isArray(raw) ? raw[0] : raw;
  return v && v.startsWith("/") && !v.startsWith("//") ? v : "/practice";
}

const ICONS: Record<string, React.ReactNode> = {
  github: (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
      <path d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.77.11 3.06.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z" />
    </svg>
  ),
  google: (
    <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true">
      <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.24 1.4-1.66 4.1-5.5 4.1-3.31 0-6-2.74-6-6.2s2.69-6.2 6-6.2c1.88 0 3.15.8 3.87 1.49l2.64-2.54C16.82 3.2 14.62 2.2 12 2.2 6.6 2.2 2.2 6.6 2.2 12S6.6 21.8 12 21.8c6.93 0 9.52-4.87 9.52-7.42 0-.5-.05-.88-.12-1.26H12Z" />
    </svg>
  ),
};

export default async function LoginPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const callbackUrl = safeCallback(params.callbackUrl);
  const session = await auth();
  if (session?.user) redirect(callbackUrl);
  const error = typeof params.error === "string" ? params.error : null;

  return (
    <div className="grid gap-10 py-6 md:grid-cols-12 md:py-12">
      <div className="md:col-span-6">
        <p className="label mb-4 flex items-center gap-3"><span className="inline-block h-px w-10 bg-accent" />Sign in</p>
        <h1 className="font-display text-5xl font-bold leading-[0.95] tracking-tight text-ink-50 sm:text-6xl">
          Your reasoning,<br /><span className="text-accent">versioned.</span>
        </h1>
        <p className="mt-6 max-w-md text-ink-300">
          An account keeps your per-skill rating, answer history and skips across devices — so each drill lands just past what you can already do.
        </p>
        <pre className="mt-8 hidden border-l-2 border-ink-700 pl-4 font-mono text-[12.5px] leading-6 text-ink-400 sm:block" aria-hidden="true">
{`skill  = weakest(mastery)
level  = difficulty(mastery[skill] + offset)
next() → unseen(skill, level, lang)`}
        </pre>
      </div>

      <div className="md:col-span-5 md:col-start-8">
        <div className="card p-6 sm:p-8">
          <div className="mb-6 flex items-center gap-3 border-b border-ink-700 pb-5">
            <LogoMark className="h-9 w-9" />
            <div>
              <div className="font-display text-lg font-semibold text-ink-50">{SITE.name}</div>
              <div className="label">{SITE.tagline}</div>
            </div>
          </div>

          {error && (
            <p role="alert" className="mb-4 border-l-2 border-signal pl-3 text-sm text-signal-soft">
              Sign-in failed ({error}). Try again.
            </p>
          )}

          {availableProviders.length === 0 ? (
            <div className="border border-dashed border-ink-600 p-4 text-sm text-ink-200" data-testid="no-providers">
              <div className="label mb-1 text-signal">status: not_configured</div>
              Sign-in isn&apos;t configured yet. GitHub and Google OAuth credentials still need to be added by the site owner.
            </div>
          ) : (
            <div className="space-y-3">
              {availableProviders.map((p) => (
                <form key={p.id} action={async () => { "use server"; await signIn(p.id, { redirectTo: callbackUrl }); }}>
                  <button type="submit" className="btn-ghost w-full justify-between px-4 py-3 text-[13px] text-ink-50" data-provider={p.id}>
                    <span className="flex items-center gap-3">{ICONS[p.id]}Continue with {p.name}</span>
                    <span className="btn-arrow">→</span>
                  </button>
                </form>
              ))}
            </div>
          )}
          <p className="mt-6 text-xs text-ink-500">We store your name, email and avatar to identify your account. Email is never shown publicly.</p>
        </div>
      </div>
    </div>
  );
}
