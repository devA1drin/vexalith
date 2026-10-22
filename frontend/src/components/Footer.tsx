import Link from "next/link";
import { LogoMark } from "@/components/Logo";
import { SITE } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-ink-700 bg-ink-950">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 sm:grid-cols-3 sm:px-6">
        <div className="flex items-center gap-3">
          <LogoMark className="h-6 w-6" />
          <div>
            <div className="font-display font-semibold text-ink-50">{SITE.name}</div>
            <div className="font-mono text-[11px] uppercase tracking-widest text-ink-400">{SITE.tagline}</div>
          </div>
        </div>
        <nav aria-label="Footer" className="flex gap-5 font-mono text-[12px] uppercase tracking-wider text-ink-400 sm:justify-center">
          <Link href="/practice" className="hover:text-accent">Practice</Link>
          <Link href="/daily" className="hover:text-accent">Daily</Link>
          <Link href="/progress" className="hover:text-accent">Progress</Link>
          <Link href="/feedback" className="hover:text-accent">Feedback</Link>
        </nav>
        <p className="font-mono text-[11px] text-ink-500 sm:text-right">© {new Date().getFullYear()} {SITE.name} · py · js · php · c++ · html · css</p>
      </div>
    </footer>
  );
}
