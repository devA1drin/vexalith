"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links: { href: string; label: string; n: string; also?: string[] }[] = [
  { href: "/practice", label: "Practice", n: "01" },
  { href: "/code", label: "Code", n: "02" },
  { href: "/daily", label: "Daily", n: "03" },
  { href: "/progress", label: "Progress", n: "04", also: ["/badges", "/leaderboard"] },
  { href: "/feedback", label: "Feedback", n: "05" },
];

export function NavLinks() {
  const pathname = usePathname();
  return (
    <nav aria-label="Primary" className="order-last flex w-full gap-0 border-t border-ink-800 pt-2 sm:order-2 sm:w-auto sm:border-0 sm:pt-0">
      {links.map((l) => {
        const active = [l.href, ...(l.also ?? [])].some((h) => pathname === h || pathname.startsWith(`${h}/`));
        return (
          <Link
            key={l.href}
            href={l.href}
            aria-current={active ? "page" : undefined}
            className={`group relative px-2.5 py-1.5 font-mono sm:px-3 text-[12px] uppercase tracking-wider transition-colors ${active ? "text-accent" : "text-ink-300 hover:text-ink-50"}`}
          >
            <span className="mr-1.5 text-ink-500 max-sm:hidden">{l.n}</span>{l.label}
            <span className={`absolute inset-x-3 -bottom-[13px] hidden h-px bg-accent transition-transform duration-200 sm:block ${active ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"}`} style={{ transformOrigin: "left" }} />
          </Link>
        );
      })}
    </nav>
  );
}
