"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/practice", label: "Practice", n: "01" },
  { href: "/daily", label: "Daily", n: "02" },
  { href: "/progress", label: "Progress", n: "03" },
  { href: "/feedback", label: "Feedback", n: "04" },
];

export function NavLinks() {
  const pathname = usePathname();
  return (
    <nav aria-label="Primary" className="order-last flex w-full gap-0 border-t border-ink-800 pt-2 sm:order-2 sm:w-auto sm:border-0 sm:pt-0">
      {links.map((l) => {
        const active = pathname === l.href || pathname.startsWith(`${l.href}/`);
        return (
          <Link
            key={l.href}
            href={l.href}
            aria-current={active ? "page" : undefined}
            className={`group relative px-3 py-1.5 font-mono text-[12px] uppercase tracking-wider transition-colors ${active ? "text-accent" : "text-ink-300 hover:text-ink-50"}`}
          >
            <span className="mr-1.5 text-ink-500">{l.n}</span>{l.label}
            <span className={`absolute inset-x-3 -bottom-[13px] hidden h-px bg-accent transition-transform duration-200 sm:block ${active ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"}`} style={{ transformOrigin: "left" }} />
          </Link>
        );
      })}
    </nav>
  );
}
