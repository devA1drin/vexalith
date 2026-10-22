/** Decorative logic-gate / trace field. Pure SVG + CSS (pulses travel along traces). */
const TRACES = [
  { d: "M0 60 H140 V140 H300 V90 H520", dur: "7s", delay: "0s" },
  { d: "M0 220 H90 V180 H260 V250 H520", dur: "9s", delay: "1.4s" },
  { d: "M520 30 H400 V140 H300", dur: "6s", delay: "2.2s" },
  { d: "M60 320 V260 H180 V180", dur: "8s", delay: "3.1s" },
  { d: "M520 320 H430 V250 H260", dur: "10s", delay: ".8s" },
];

export function CircuitField({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 520 340" preserveAspectRatio="xMidYMid slice" className={className} aria-hidden="true">
      {TRACES.map((t, i) => (
        <g key={i}>
          <path d={t.d} className="trace" />
          <path d={t.d} className="trace-pulse" style={{ ["--d" as string]: t.dur, ["--delay" as string]: t.delay }} />
        </g>
      ))}
      {/* AND gate */}
      <path d="M290 125 h12 a15 15 0 0 1 0 30 h-12 z" className="gate gate-on" style={{ ["--d" as string]: "7s" }} />
      {/* OR gate */}
      <path d="M250 235 q10 15 0 30 q22 0 34 -15 q-12 -15 -34 -15 z" className="gate gate-on" style={{ ["--d" as string]: "9s", ["--delay" as string]: "1.4s" }} />
      {/* NOT gate */}
      <path d="M170 172 l16 8 l-16 8 z" className="gate gate-on" style={{ ["--d" as string]: "8s", ["--delay" as string]: "3.1s" }} />
      {[[140, 60], [300, 90], [90, 220], [400, 140], [60, 320], [430, 250]].map(([x, y], i) => (
        <rect key={i} x={x - 2.5} y={y - 2.5} width="5" height="5" fill="#0c0d0c" stroke="rgba(242,241,236,.25)" />
      ))}
    </svg>
  );
}
