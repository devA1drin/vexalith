import { LogoMark } from "@/components/Logo";
import { SITE } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-ink-700 bg-ink-950">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 sm:grid-cols-2 sm:px-6">
        <div className="flex items-center gap-3">
          <LogoMark className="h-6 w-6" />
          <div>
            <div className="font-display font-semibold text-ink-50">{SITE.name}</div>
            <div className="font-mono text-[11px] uppercase tracking-widest text-ink-400">{SITE.tagline}</div>
          </div>
        </div>
        <p className="font-mono text-[11px] text-ink-500 sm:text-right">© {new Date().getFullYear()} {SITE.name} · py · js · php · c++ · java · html · css</p>
      </div>
    </footer>
  );
}
