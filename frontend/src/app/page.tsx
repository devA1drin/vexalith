import Link from "next/link";
import { auth } from "@/auth";
import { Hero } from "@/components/Hero";
import { Reveal } from "@/components/Reveal";

const DOMAINS = [
  { n: "01", name: "Code Tracing", ask: "What does this print, line by line?", code: "print(f(1)); print(f(2))" },
  { n: "02", name: "Debugging", ask: "Find the root cause, not the symptom.", code: "for (var i=0;i<3;i++) setTimeout(()=>log(i))" },
  { n: "03", name: "Algorithmic Thinking", ask: "Defend the Big-O. Propose better.", code: "if x in big_list:  # O(?)" },
  { n: "04", name: "Edge Cases & Testing", ask: "Which input breaks it?", code: "avg = sum(xs) / len(xs)" },
  { n: "05", name: "Code Review & Design", ask: "What would you change before merge?", code: "function calc(a, b, mode, flag2) {…}" },
  { n: "06", name: "Data Structures", ask: "Pick the right shape for the data.", code: "queue.pop(0)  # cost?" },
];

const CODE = [
  ["def", " f(x, acc=[]):"],
  ["    ", "acc.append(x)"],
  ["    return", " acc"],
  ["", ""],
  ["print", "(f(1))"],
  ["print", "(f(2))"],
];

export default async function HomePage() {
  const session = await auth();
  const cta = session?.user ? "/practice" : "/login?callbackUrl=/practice";
  return (
    <div className="space-y-24">
      <Hero ctaHref={cta} signedIn={!!session?.user} />

      {/* Trace runner: a real snippet executing */}
      <section className="grid gap-10 md:grid-cols-12">
        <Reveal className="md:col-span-4">
          <p className="label mb-3">Specimen · code_tracing / intermediate</p>
          <h2 className="font-display text-3xl font-bold tracking-tight text-ink-50">Follow the interpreter, not your intuition.</h2>
          <p className="mt-4 text-ink-300">
            Default arguments are evaluated once. The second call prints <code className="font-mono text-accent">[1, 2]</code>.
            Vexalith asks you to explain <em>why</em> — and checks that your explanation names the shared list.
          </p>
        </Reveal>
        <Reveal delay={120} className="md:col-span-8">
          <div className="panel grid sm:grid-cols-[1fr_200px]">
            <div className="border-b border-ink-700 sm:border-b-0 sm:border-r">
              <div className="flex items-center justify-between border-b border-ink-700 px-4 py-2">
                <span className="label">mutable_default.py</span>
                <span className="label text-accent">● running</span>
              </div>
              <div className="relative p-4 font-mono text-[13px]">
                <div className="relative">
                  <span className="exec-line" aria-hidden="true" />
                  {CODE.map(([kw, rest], i) => (
                    <div key={i} className="relative flex h-6 items-center">
                      <span className="w-7 select-none text-ink-600">{i + 1}</span>
                      <span className="whitespace-pre">
                        <span className="text-accent">{kw}</span>
                        <span className="text-ink-100">{rest}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div>
              <div className="border-b border-ink-700 px-4 py-2"><span className="label">stdout</span></div>
              <div className="space-y-1 p-4 font-mono text-[13px]">
                <div className="out-1 text-ink-100">[1]</div>
                <div className="out-2 text-signal-soft">[1, 2]  <span className="text-ink-500">← why?</span></div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Domains as an index, not cards */}
      <section>
        <Reveal className="mb-6 flex items-end justify-between gap-4 border-b border-ink-700 pb-4">
          <h2 className="font-display text-3xl font-bold tracking-tight text-ink-50">Six ways code goes wrong.<br className="hidden sm:block" /> Six drills to catch it.</h2>
          <span className="label hidden sm:block">72 questions · 3 levels · py / js</span>
        </Reveal>
        <ol>
          {DOMAINS.map((d, i) => (
            <Reveal as="li" key={d.n} delay={i * 60} className="group grid items-baseline gap-2 border-b border-ink-800 py-5 transition-colors hover:bg-ink-900 sm:grid-cols-12 sm:gap-6 sm:px-2">
              <span className="font-mono text-sm text-ink-500 group-hover:text-accent sm:col-span-1">{d.n}</span>
              <span className="font-display text-xl font-semibold text-ink-50 sm:col-span-4">{d.name}</span>
              <span className="text-ink-300 sm:col-span-3">{d.ask}</span>
              <code className="truncate font-mono text-[12.5px] text-ink-400 group-hover:text-ink-200 sm:col-span-4">{d.code}</code>
            </Reveal>
          ))}
        </ol>
      </section>

      {/* Grading explained with a specimen */}
      <section id="how" className="grid scroll-mt-24 gap-10 md:grid-cols-12">
        <Reveal className="md:col-span-5 md:col-start-1">
          <p className="label mb-3">How grading works</p>
          <h2 className="font-display text-3xl font-bold tracking-tight text-ink-50">Right answer, weak reason? That&apos;s a partial.</h2>
          <ul className="mt-6 space-y-4 text-ink-300">
            <li><span className="font-mono text-accent">70%</span> correctness — did you reach the right result?</li>
            <li><span className="font-mono text-accent">30%</span> reasoning — did you name the mechanism (aliasing, closure capture, off-by-one)?</li>
            <li><span className="font-mono text-signal">−12%</span> per misconception detected in your explanation.</li>
          </ul>
          <p className="mt-6 text-sm text-ink-400">Difficulty adapts per skill with an Elo-style rating. Skips are tracked but barely move your score.</p>
        </Reveal>
        <Reveal delay={150} className="md:col-span-6 md:col-start-7">
          <div className="panel p-6">
            <div className="flex items-baseline justify-between border-b border-ink-700 pb-4">
              <span className="label">feedback.json</span>
              <span className="font-display text-4xl font-bold text-ink-50">74<span className="text-ink-500">/100</span></span>
            </div>
            {[["correctness", 0.9], ["reasoning", 0.45]].map(([k, v], i) => (
              <div key={k as string} className="mt-5">
                <div className="mb-1.5 flex justify-between font-mono text-[12px] uppercase tracking-wider"><span className="text-ink-300">{k}</span><span className="text-ink-50">{Math.round((v as number) * 100)}</span></div>
                <div className="h-1.5 bg-ink-800"><div className="bar-grow h-full bg-accent" style={{ width: `${(v as number) * 100}%`, ["--rd" as string]: `${300 + i * 200}ms` }} /></div>
              </div>
            ))}
            <div className="mt-6 border-l-2 border-signal pl-3 text-sm">
              <div className="font-mono text-[11px] uppercase tracking-wider text-signal">missed</div>
              <p className="mt-1 text-ink-200">Say that the default list is created once, at definition time.</p>
            </div>
          </div>
        </Reveal>
      </section>

      <Reveal as="section" className="flex flex-col items-start justify-between gap-6 border border-accent p-8 sm:flex-row sm:items-center">
        <div>
          <h2 className="font-display text-2xl font-bold text-ink-50 sm:text-3xl">One question takes about two minutes.</h2>
          <p className="mt-1 text-ink-300">Pick Python or JavaScript. Explain your thinking. See exactly where it held and where it broke.</p>
        </div>
        <Link href={cta} className="btn-primary shrink-0 px-6 py-3">Start a drill <span className="btn-arrow">→</span></Link>
      </Reveal>
    </div>
  );
}
