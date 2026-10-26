/** Small, plain date/time helpers shared by Review and Timed quiz. */

export function mmss(seconds: number): string {
  const s = Math.max(0, Math.ceil(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export function shortDate(iso: string | null | undefined): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/** "today", "yesterday", "3 days ago", or a date for anything older than a week. */
export function ago(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return "";
  const then = new Date(iso);
  const days = Math.floor((startOfDay(now) - startOfDay(then.getTime())) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  return shortDate(iso);
}

/** "tomorrow", "in 3 days", or a date. */
export function until(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return "";
  const days = Math.ceil((startOfDay(new Date(iso).getTime()) - startOfDay(now)) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "tomorrow";
  if (days < 7) return `in ${days} days`;
  return `on ${shortDate(iso)}`;
}

function startOfDay(ms: number): number {
  const d = new Date(ms);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}

export const LEVEL: Record<string, number> = { beginner: 1, intermediate: 2, advanced: 3 };
