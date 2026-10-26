import type { ReviewFilters } from "@/lib/api";

export const FILTER_KEYS = ["topic", "language", "path", "difficulty", "kind"] as const;

export function filtersQuery(f: ReviewFilters, extra: Record<string, string> = {}): string {
  const q = new URLSearchParams();
  for (const k of FILTER_KEYS) if (f[k]) q.set(k, f[k] as string);
  for (const [k, v] of Object.entries(extra)) q.set(k, v);
  const s = q.toString();
  return s ? `?${s}` : "";
}

export function readFilters(search: string): ReviewFilters {
  const q = new URLSearchParams(search);
  const f: ReviewFilters = {};
  for (const k of FILTER_KEYS) {
    const v = q.get(k);
    if (v) (f as Record<string, string>)[k] = v.slice(0, 64);
  }
  return f;
}
