"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Avatar } from "@/components/Avatar";
import { useProfile } from "@/lib/profileStore";

/** The learner's mark in the header; opens Profile, Bookmarks and Sign out. */
export function ProfileMenu({ fallbackName, children }: { fallbackName: string; children: ReactNode }) {
  const profile = useProfile();
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("mousedown", away);
      document.removeEventListener("keydown", esc);
    };
  }, [open]);

  const name = profile?.shown_name ?? fallbackName;
  const items = [
    { href: "/profile", label: "Profile" },
    { href: "/bookmarks", label: "Bookmarks" },
    ...(profile?.is_admin ? [{ href: "/admin", label: "Admin" }] : []),
  ];
  return (
    <div ref={box} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`Account menu for ${name}`}
        className={`flex items-center gap-2 border py-0.5 pl-0.5 pr-2 transition-colors ${open ? "border-accent" : "border-ink-700 hover:border-ink-400"}`}
        data-testid="profile-menu"
      >
        <Avatar mark={profile?.avatar ?? "initials-ink"} name={name} photoUrl={profile?.photo_url} size={26} />
        <span className="hidden max-w-[9rem] truncate text-sm text-ink-200 md:inline">{name}</span>
        <svg viewBox="0 0 10 6" width="9" height="6" aria-hidden="true" className={`text-ink-400 transition-transform ${open ? "rotate-180" : ""}`}>
          <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" />
        </svg>
      </button>
      {open && (
        <div role="menu" className="absolute right-0 top-[calc(100%+8px)] z-50 w-56 border border-ink-600 bg-ink-950 shadow-[6px_6px_0_0_rgba(0,0,0,0.5)]" data-testid="profile-menu-list">
          <div className="border-b border-ink-800 px-3 py-2.5">
            <div className="truncate text-sm text-ink-50">{name}</div>
            {profile && (
              <div className="truncate font-mono text-[11px] text-ink-500">
                {profile.visibility === "hidden" ? "Off the leaderboard" : `Ranks as ${profile.leaderboard_name}`}
              </div>
            )}
          </div>
          {items.map((it) => (
            <Link
              key={it.href}
              role="menuitem"
              href={it.href}
              className={`block px-3 py-2 font-mono text-[12px] uppercase tracking-wider hover:bg-ink-900 hover:text-accent ${pathname.startsWith(it.href) ? "text-accent" : "text-ink-200"}`}
            >
              {it.label}
            </Link>
          ))}
          <div className="border-t border-ink-800" role="none">{children}</div>
        </div>
      )}
    </div>
  );
}
