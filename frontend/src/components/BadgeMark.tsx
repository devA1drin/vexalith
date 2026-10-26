import type { BadgeGroup } from "@/lib/api";

/**
 * Custom badge marks: a frame per group (answers = chamfered plate, streaks = hexagon,
 * languages = shield, code = terminal window, paths = route marker) and a line-art glyph or
 * short mono label.
 * Earned marks are lime; locked ones are graphite with a dashed frame.
 */

const FRAMES: Record<BadgeGroup, string> = {
  answers: "M20 4H44L60 20V44L44 60H20L4 44V20Z",
  streaks: "M32 3L57 17.5V46.5L32 61L7 46.5V17.5Z",
  languages: "M8 6H56V40L32 60L8 40Z",
  code: "M6 8H58V56H6Z",
  paths: "M32 3L61 32L32 61L3 32Z",
};
const INNER: Record<BadgeGroup, string> = {
  answers: "M22 9H42L55 22V42L42 55H22L9 42V22Z",
  streaks: "M32 8.5L52 20V44L32 55.5L12 44V20Z",
  languages: "M13 11H51V38L32 54L13 38Z",
  code: "M11 18H53V51H11Z",
  paths: "M32 9.5L54.5 32L32 54.5L9.5 32Z",
};

/** Short labels drawn in mono type inside the mark. */
const LABELS: Record<string, string> = {
  "ten-correct": "10",
  "fifty-correct": "50",
  "streak-3": "3",
  "streak-7": "7",
  "streak-30": "30",
  "cpp-answer": "C++",
  "java-answer": "JAVA",
  filipino: "FIL",
  "ex-python": "py",
  "ex-javascript": "js",
  "ex-cpp": "c++",
  "ex-java": "java",
  "ex-php": "php",
};

function Glyph({ id, color }: { id: string; color: string }) {
  const s = { fill: "none", stroke: color, strokeWidth: 2.4, strokeLinecap: "square" as const, strokeLinejoin: "miter" as const };
  switch (id) {
    case "first-correct": // a checked node
      return (
        <>
          <path d="M20 33L28 41L44 24" {...s} strokeWidth={3} />
        </>
      );
    case "advanced": // three bars, the last one lit: the hardest level
      return (
        <>
          <path d="M21 42V36M31 42V29" {...s} />
          <path d="M41 42V20" {...s} strokeWidth={4} />
        </>
      );
    case "mastery": // a full gauge
      return (
        <>
          <path d="M19 40A14 14 0 1 1 45 40" {...s} />
          <path d="M32 33L41 25" {...s} />
          <rect x="30" y="31" width="4" height="4" fill={color} />
        </>
      );
    case "daily-first": // a calendar grid with today filled
      return (
        <>
          <path d="M19 22H45V44H19ZM19 29H45M28 29V44M37 29V44M19 36.5H45" {...s} strokeWidth={1.8} />
          <rect x="37.5" y="37" width="7" height="6.5" fill={color} />
        </>
      );
    case "oop-answer": // a small class diagram
      return (
        <>
          <path d="M26 17H38V26H26ZM15 36H27V45H15ZM37 36H49V45H37ZM32 26V31H21V36M32 31H43V36" {...s} strokeWidth={1.8} />
        </>
      );
    case "unassisted": // a path breaking through a limit line: no help needed
      return (
        <>
          <path d="M36 20V44" stroke={color} strokeWidth={1.6} strokeDasharray="3 3" />
          <path d="M18 40L46 24M38 23L46 24L43 31" {...s} />
        </>
      );
    case "polyglot": // five languages around one idea
      return (
        <>
          <circle cx="32" cy="33" r="11" {...s} strokeWidth={1.6} />
          {[0, 72, 144, 216, 288].map((a) => {
            const r = (a - 90) * (Math.PI / 180);
            return <rect key={a} x={32 + 11 * Math.cos(r) - 3} y={33 + 11 * Math.sin(r) - 3} width="6" height="6" fill={color} />;
          })}
        </>
      );
    case "path-step": // a route out of its first, filled node
      return (
        <>
          <path d="M23 38H31V28H39" {...s} strokeWidth={2} />
          <rect x="18" y="35" width="6" height="6" fill={color} />
          <rect x="39" y="25" width="6" height="6" fill="none" stroke={color} strokeWidth={1.6} />
        </>
      );
    case "path-finisher": // a route that ends at a flag
      return (
        <>
          <path d="M18 40H26V32H33" {...s} strokeWidth={2} strokeDasharray="3 2.5" />
          <path d="M36 20V44" {...s} strokeWidth={2} />
          <path d="M36.5 21H46L43 25.5L46 30H36.5Z" fill={color} />
        </>
      );
    case "path-three": // three routes meeting at one point
      return (
        <>
          <path d="M32 32L20 24M32 32L44 24M32 32V45" {...s} strokeWidth={1.8} />
          <rect x="17" y="21" width="5" height="5" fill={color} />
          <rect x="42" y="21" width="5" height="5" fill={color} />
          <rect x="29.5" y="43" width="5" height="5" fill={color} />
          <rect x="29" y="29" width="6" height="6" fill="none" stroke={color} strokeWidth={1.6} />
        </>
      );
    default:
      return null;
  }
}

export function BadgeMark({ id, group, earned, size = 56, title }: { id: string; group: BadgeGroup; earned: boolean; size?: number; title?: string }) {
  const color = earned ? "#c8f031" : "#4a4a46";
  const label = LABELS[id];
  const isCode = group === "code";
  const textY = group === "languages" ? 34 : isCode ? 40 : 37;
  const fontSize = !label ? 0 : label.length >= 4 ? 11 : label.length === 3 ? 14 : 19;
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} role={title ? "img" : undefined} aria-hidden={title ? undefined : true} aria-label={title}>
      <path d={FRAMES[group]} fill={earned ? "rgba(200,240,49,0.08)" : "#121312"} stroke={color} strokeWidth={2} strokeDasharray={earned ? undefined : "4 3"} />
      <path d={INNER[group]} fill="none" stroke={color} strokeOpacity={earned ? 0.35 : 0.5} strokeWidth={1} />
      {isCode && (
        <>
          <rect x="11" y="11.5" width="3" height="3" fill={color} />
          <rect x="16" y="11.5" width="3" height="3" fill={color} fillOpacity={0.5} />
        </>
      )}
      {group === "streaks" && label && <path d="M24 46H40" stroke={color} strokeWidth={2} />}
      {label ? (
        <text x="32" y={textY} textAnchor="middle" dominantBaseline="middle" fill={color} fontFamily="var(--font-mono), ui-monospace, monospace" fontWeight={700} fontSize={fontSize} letterSpacing={label.length >= 4 ? 0.5 : 0}>
          {label}
        </text>
      ) : (
        <Glyph id={id} color={color} />
      )}
    </svg>
  );
}

/** The level mark: a hexagon with the level number, used in the header and on the level card. */
export function LevelMark({ level, size = 40 }: { level: number; size?: number }) {
  const n = String(level);
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} aria-hidden>
      <path d="M32 3L57 17.5V46.5L32 61L7 46.5V17.5Z" fill="#c8f031" />
      <path d="M32 9L52 20.5V43.5L32 55L12 43.5V20.5Z" fill="none" stroke="#0c0d0c" strokeOpacity={0.35} strokeWidth={1.5} />
      <text x="32" y="34" textAnchor="middle" dominantBaseline="middle" fill="#0c0d0c" fontFamily="var(--font-mono), ui-monospace, monospace" fontWeight={800} fontSize={n.length > 1 ? 22 : 28}>
        {n}
      </text>
    </svg>
  );
}
