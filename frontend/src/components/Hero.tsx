import Link from "next/link";
import { CircuitField } from "@/components/CircuitField";

function Compile({ text }: { text: string }) {
  return (
    <span aria-hidden="true">
      {Array.from(text).map((c, i) => (
        <span key={i} className="compile-char" style={{ ["--i" as string]: i }}>
          {c === " " ? "\u00a0" : c}
        </span>
      ))}
    </span>
  );
}

const SHARDS = [
  { dx: "40px", dy: "-46px", r: "40deg" }, { dx: "70px", dy: "-12px", r: "-30deg" }, { dx: "56px", dy: "30px", r: "70deg" },
  { dx: "22px", dy: "52px", r: "-60deg" }, { dx: "90px", dy: "8px", r: "20deg" }, { dx: "30px", dy: "-70px", r: "90deg" },
];

export function Hero({ ctaHref, signedIn }: { ctaHref: string; signedIn: boolean }) {
  return (
    <section className="relative -mx-4 border-b border-ink-700 px-4 pb-14 pt-10 sm:pt-16">
      <CircuitField className="pointer-events-none absolute inset-y-0 right-0 hidden h-full w-[55%] opacity-90 md:block" />
      <div className="relative grid gap-10 md:grid-cols-12">
        <div className="md:col-span-8">
          <p className="label mb-6 flex items-center gap-3">
            <span className="inline-block h-px w-10 bg-accent" /> v1 · reasoning drills for programmers
          </p>
          <h1 className="font-display text-[clamp(2.8rem,9vw,6.4rem)] font-bold leading-[0.92] tracking-[-0.035em] text-ink-50">
            <span className="sr-only">Build Logic. Break Limits.</span>
            <span className="block whitespace-nowrap">
              <Compile text="Build Logic." />
              <span className="compile-caret" aria-hidden="true" />
            </span>
            <span className="mt-1 block whitespace-nowrap" aria-hidden="true">
            <span className="limit-zone inline-block" style={{ ["--limit" as string]: "70%" }}>
              <span className="limit-tag font-mono text-[11px] font-normal uppercase tracking-widest text-signal">max_depth</span>
              <span className="break-text text-accent">Break Limits.</span>
              <span className="limit-line"><i /><i /></span>
              {SHARDS.map((s, i) => (
                <span key={i} className="shard" style={{ ["--dx" as string]: s.dx, ["--dy" as string]: s.dy, ["--r" as string]: s.r }} />
              ))}
            </span>
            </span>
          </h1>

          <div className="mt-8 max-w-md" aria-hidden="true">
            <div className="mb-1.5 flex justify-between font-mono text-[11px] uppercase tracking-widest text-ink-400">
              <span>reasoning.capacity</span>
              <span className="overflow-count text-accent" />
            </div>
            <div className="overflow-track"><div className="overflow-fill" /></div>
          </div>

          <p className="mt-8 max-w-xl text-lg leading-relaxed text-ink-300">
            Read real Python, JavaScript, PHP, HTML and CSS. Predict the output, find the bug, defend the Big-O, crack the logic puzzle.
            Every answer is graded twice — <span className="text-ink-50">is it right</span>, and <span className="text-ink-50">is your reasoning sound</span>.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link href={ctaHref} className="btn-primary px-5 py-3">
              {signedIn ? "Resume practice" : "Start a drill"} <span className="btn-arrow">→</span>
            </Link>
            <Link href="#how" className="btn-ghost px-4 py-3">How grading works</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
