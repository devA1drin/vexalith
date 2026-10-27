/** Generated avatar marks: no uploads, just the learner's initials or a pattern drawn from their name. */

export const MARK_LABELS: Record<string, string> = {
  "initials-lime": "Lime initials",
  "initials-ink": "Graphite initials",
  "initials-signal": "Orange initials",
  "initials-outline": "Outline initials",
  "mark-grid": "Grid",
  "mark-circuit": "Circuit",
  "mark-stripes": "Stripes",
  "mark-dots": "Dots",
  "mark-bracket": "Brackets",
  "mark-stack": "Stack",
  photo: "Sign-in photo",
};

/** Up to two letters: first and last word, or the first two letters of a single word. */
export function initials(name: string | null | undefined): string {
  const words = (name ?? "").normalize("NFKC").replace(/[^\p{L}\p{N}\s'-]/gu, " ").trim().split(/\s+/).filter(Boolean);
  if (!words.length) return "?";
  const first = Array.from(words[0]);
  if (words.length === 1) return first.slice(0, 2).join("").toUpperCase();
  return (first[0] + Array.from(words[words.length - 1])[0]).toUpperCase();
}

/** A small stable hash, so a pattern looks the same every time for the same name. */
export function seedOf(text: string): number {
  let h = 2166136261;
  for (const ch of text) {
    h ^= ch.codePointAt(0) ?? 0;
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** Which cells of a symmetric 5×5 grid are filled (mirrored left to right, like a stamp). */
export function gridCells(seed: number): boolean[] {
  const cells: boolean[] = [];
  for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 5; col++) {
      const c = col < 3 ? col : 4 - col;
      cells.push(((seed >>> (row * 3 + c)) & 1) === 1);
    }
  }
  if (!cells.some(Boolean)) cells[12] = true;
  return cells;
}
