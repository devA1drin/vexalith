"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/practice", label: "Practice" },
  { href: "/progress", label: "Progress" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="border-b border-ink-800/40 bg-ink-950/80 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-semibold tracking-tight text-ink-50">
          Critical<span className="text-accent">Thinking</span>
          <span className="ml-2 text-xs font-normal text-ink-400">Adaptive MVP</span>
        </Link>
        <nav className="flex gap-1">
          {links.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-md px-3 py-1.5 text-sm transition ${
                  active
                    ? "bg-ink-800 text-accent-soft"
                    : "text-ink-300 hover:bg-ink-900 hover:text-ink-50"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
