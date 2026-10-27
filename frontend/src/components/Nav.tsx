import Link from "next/link";
import { auth, signOut } from "@/auth";
import { Wordmark } from "@/components/Logo";
import { NavLinks } from "@/components/NavLinks";
import { ProfileMenu } from "@/components/ProfileMenu";
import { XpChip } from "@/components/XpChip";

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
              <XpChip />
              <ProfileMenu fallbackName={user.name && !user.name.includes("@") ? user.name : "Learner"}>
                <form action={async () => { "use server"; await signOut({ redirectTo: "/" }); }}>
                  <button type="submit" role="menuitem" className="block w-full px-3 py-2 text-left font-mono text-[12px] uppercase tracking-wider text-ink-300 hover:bg-ink-900 hover:text-signal-soft" data-testid="sign-out">
                    Sign out
                  </button>
                </form>
              </ProfileMenu>
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
