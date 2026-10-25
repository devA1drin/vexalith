/** A short, plain-language "what is this page and what do I do here" intro. */
export function PageIntro({ steps, children }: { steps?: string[]; children: React.ReactNode }) {
  return (
    <div className="max-w-3xl space-y-3" data-testid="page-intro">
      <p className="text-[15px] leading-relaxed text-ink-300">{children}</p>
      {steps && steps.length > 0 && (
        <ol className="flex flex-wrap gap-x-5 gap-y-1.5 font-mono text-[12px] text-ink-400">
          {steps.map((s, i) => (
            <li key={s} className="flex items-baseline gap-2">
              <span className="text-accent">{String(i + 1).padStart(2, "0")}</span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
