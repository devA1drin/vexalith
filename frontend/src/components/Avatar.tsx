import { gridCells, initials, seedOf } from "@/lib/avatar";

const LIME = "#c8f031";
const INK = "#0c0d0c";
const INK_800 = "#222322";
const INK_600 = "#4a4a46";
const PAPER = "#f2f1ec";
const SIGNAL = "#ff5b2e";

/**
 * A learner's mark: their sign-in photo (only if they chose it), else generated initials or a
 * pattern drawn from their name. Square, like the rest of the site.
 */
export function Avatar({
  mark,
  name,
  photoUrl,
  size = 28,
  className = "",
}: {
  mark: string | null | undefined;
  name: string | null | undefined;
  photoUrl?: string | null;
  size?: number;
  className?: string;
}) {
  if (mark === "photo" && photoUrl) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img src={photoUrl} alt="" width={size} height={size} referrerPolicy="no-referrer"
        className={`shrink-0 border border-ink-600 object-cover ${className}`} style={{ width: size, height: size }} />
    );
  }
  const key = mark && mark !== "photo" ? mark : "initials-ink";
  const text = initials(name);
  const seed = seedOf(name || "?");
  return (
    <svg viewBox="0 0 40 40" width={size} height={size} aria-hidden="true" className={`shrink-0 ${className}`} data-mark={key}>
      <Body mark={key} text={text} seed={seed} />
    </svg>
  );
}

function Letters({ text, fill, size = 16 }: { text: string; fill: string; size?: number }) {
  return (
    <text x="20" y="21" textAnchor="middle" dominantBaseline="middle" fill={fill}
      style={{ font: `700 ${size}px var(--font-mono), ui-monospace, monospace`, letterSpacing: "-0.5px" }}>
      {text}
    </text>
  );
}

function Body({ mark, text, seed }: { mark: string; text: string; seed: number }) {
  switch (mark) {
    case "initials-lime":
      return (<><rect width="40" height="40" fill={LIME} /><Letters text={text} fill={INK} /></>);
    case "initials-signal":
      return (<><rect width="40" height="40" fill={SIGNAL} /><Letters text={text} fill={INK} /></>);
    case "initials-outline":
      return (<><rect x="1" y="1" width="38" height="38" fill={INK} stroke={LIME} strokeWidth="2" /><Letters text={text} fill={LIME} /></>);
    case "mark-grid": {
      const cells = gridCells(seed);
      return (
        <>
          <rect width="40" height="40" fill={INK_800} />
          {cells.map((on, i) => on && <rect key={i} x={5 + (i % 5) * 6} y={5 + Math.floor(i / 5) * 6} width="6" height="6" fill={LIME} />)}
        </>
      );
    }
    case "mark-circuit": {
      const y1 = 10 + (seed % 3) * 5;
      const y2 = 22 + ((seed >>> 3) % 3) * 4;
      const x = 14 + ((seed >>> 6) % 3) * 5;
      return (
        <>
          <rect width="40" height="40" fill={INK} />
          <path d={`M0 ${y1}H${x}V${y2}H40M${x} ${y2}V40`} stroke={LIME} strokeWidth="2" fill="none" />
          <path d={`M40 ${y1 - 4}H${x + 10}V0`} stroke={INK_600} strokeWidth="2" fill="none" />
          <rect x={x - 3} y={y1 - 3} width="6" height="6" fill={LIME} />
          <rect x={x + 7} y={y1 - 7} width="6" height="6" fill={INK} stroke={LIME} strokeWidth="1.5" />
        </>
      );
    }
    case "mark-stripes": {
      const gap = 6 + (seed % 3) * 2;
      const lines = [];
      for (let d = -40; d < 80; d += gap) lines.push(<path key={d} d={`M${d} 40L${d + 40} 0`} stroke={LIME} strokeWidth="2" />);
      return (<><rect width="40" height="40" fill={INK_800} />{lines}<rect x="11" y="11" width="18" height="18" fill={INK} /><Letters text={text.slice(0, 1)} fill={LIME} size={13} /></>);
    }
    case "mark-dots": {
      const dots = [];
      for (let r = 0; r < 4; r++)
        for (let c = 0; c < 4; c++) {
          const on = ((seed >>> (r * 4 + c)) & 1) === 1;
          dots.push(<circle key={`${r}${c}`} cx={8 + c * 8} cy={8 + r * 8} r={on ? 2.6 : 1.2} fill={on ? LIME : INK_600} />);
        }
      return (<><rect width="40" height="40" fill={INK} />{dots}</>);
    }
    case "mark-bracket":
      return (
        <>
          <rect width="40" height="40" fill={INK} />
          <path d="M11 8H6V32H11M29 8H34V32H29" stroke={LIME} strokeWidth="2.5" fill="none" />
          <Letters text={text} fill={PAPER} size={13} />
        </>
      );
    case "mark-stack": {
      const widths = [0, 1, 2, 3].map((i) => 12 + ((seed >>> (i * 3)) % 4) * 5);
      return (
        <>
          <rect width="40" height="40" fill={INK_800} />
          {widths.map((w, i) => <rect key={i} x="6" y={7 + i * 7} width={w} height="4" fill={i === 0 ? LIME : i === 3 ? SIGNAL : PAPER} />)}
        </>
      );
    }
    case "initials-ink":
    default:
      return (<><rect x="0.5" y="0.5" width="39" height="39" fill={INK_800} stroke={INK_600} /><Letters text={text} fill={PAPER} /></>);
  }
}
