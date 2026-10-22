import Link from "next/link";
import { auth, signOut } from "@/auth";
import { Wordmark } from "@/components/Logo";
import { NavLinks } from "@/components/NavLinks";

export async function Nav() {
  const session = await auth();
  const user = session?.user;
  return (
    <header className="sticky top-0 z-40 border-b border-ink-700 bg-ink-950/95">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-4 gap-y-2 px-4 py-3 sm:px-6">
        <Link href="/" aria-label="Vexalith home"><Wordmark /></Link>
        <div className="flex items-center gap-3 sm:order-3">
          {user ? (
            <>
              <div className="hidden items-center gap-2 md:flex">
                {user.image ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={user.image} alt="" className="h-7 w-7 border border-ink-600" referrerPolicy="no-referrer" />
                ) : (
                  <span className="flex h-7 w-7 items-center justify-center border border-ink-600 font-mono text-xs">{(user.name ?? "?").slice(0, 1).toUpperCase()}</span>
                )}
                <span className="max-w-[10rem] truncate text-sm text-ink-200">{user.name ?? user.email}</span>
              </div>
              <form action={async () => { "use server"; await signOut({ redirectTo: "/" }); }}>
                <button type="submit" className="btn-ghost">Sign out</button>
              </form>
            </>
          ) : (
            <Link href="/login" className="btn-primary px-3 py-1.5 text-[12px]">Sign in</Link>
          )}
        </div>
        <NavLinks />
      </div>
    </header>
  );
}
