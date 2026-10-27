/** Pure helpers for the admin dashboard (unit-tested). */

export function pct(v: number | null | undefined, digits = 0): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return `${(v * 100).toFixed(digits)}%`;
}

export function num(v: number | null | undefined): string {
  if (v === null || v === undefined) return "—";
  return v.toLocaleString("en-US");
}

/** A round axis maximum at or above the largest value (1, 2, 5 x 10^n). */
export function niceMax(values: number[]): number {
  const top = Math.max(0, ...values);
  if (top <= 0) return 1;
  const p = 10 ** Math.floor(Math.log10(top));
  for (const m of [1, 2, 5, 10]) if (top <= m * p) return m * p;
  return 10 * p;
}

/** Destructive actions are confirmed by typing the learner's handle; "@" and case don't matter. */
export function confirmMatches(word: string, typed: string): boolean {
  const clean = (s: string) => s.trim().replace(/^@/, "").toLowerCase();
  return clean(word) !== "" && clean(word) === clean(typed);
}

/** Query string from a filter object, dropping empty values and page 1. */
export function adminQuery(f: Record<string, string | number | undefined | null>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(f)) {
    if (v === undefined || v === null || v === "") continue;
    if (k === "page" && Number(v) <= 1) continue;
    q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

/** Rating 0-1000 to a short word. */
export function ratingBand(r: number): string {
  if (r >= 700) return "hard";
  if (r >= 400) return "medium";
  return "easy";
}

const ACTION_WORDS: Record<string, string> = {
  "learner.board_hidden": "Hid from leaderboard",
  "learner.board_shown": "Put back on leaderboard",
  "learner.xp_reset": "Reset XP",
  "learner.deleted": "Deleted learner data",
  "question.edited": "Edited question",
  "question.hidden": "Hid question",
  "question.shown": "Unhid question",
  "question.created": "Added question",
  "feedback.reviewed": "Marked feedback reviewed",
  "feedback.unreviewed": "Marked feedback new",
  "feedback.hidden": "Hid feedback from the wall",
  "feedback.shown": "Put feedback back on the wall",
  "feedback.deleted": "Deleted feedback",
};

export function actionLabel(action: string): string {
  return ACTION_WORDS[action] ?? action;
}

export function actionTone(action: string): "danger" | "edit" | "plain" {
  if (action.endsWith(".deleted") || action === "learner.xp_reset") return "danger";
  if (action.startsWith("question.")) return "edit";
  return "plain";
}
