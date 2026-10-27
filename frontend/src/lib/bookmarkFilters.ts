import type { BookmarkFilters } from "@/lib/api";

export const BOOKMARK_FILTER_KEYS = ["kind", "topic", "language"] as const;

export function bookmarkQuery(f: BookmarkFilters, extra: Record<string, string> = {}): string {
  const q = new URLSearchParams();
  for (const k of BOOKMARK_FILTER_KEYS) if (f[k]) q.set(k, f[k] as string);
  for (const [k, v] of Object.entries(extra)) q.set(k, v);
  const s = q.toString();
  return s ? `?${s}` : "";
}

export function readBookmarkFilters(search: string): BookmarkFilters {
  const q = new URLSearchParams(search);
  const f: BookmarkFilters = {};
  const kind = q.get("kind");
  if (kind === "question" || kind === "exercise") f.kind = kind;
  for (const k of ["topic", "language"] as const) {
    const v = q.get(k);
    if (v && /^[a-z0-9_-]{1,64}$/.test(v)) f[k] = v;
  }
  return f;
}

/** Where a saved item opens. */
export function bookmarkHref(b: { kind: string; id: number | null; slug: string | null; language: string }): string {
  return b.kind === "exercise" ? `/code/${b.slug}` : `/practice?${new URLSearchParams({ question: String(b.id), language: b.language })}`;
}
