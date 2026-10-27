/** The house style for question text, shown next to every editor. */
export function HouseStyle({ notes }: { notes: string[] | null }) {
  return (
    <aside className="panel space-y-4 p-4" data-testid="house-style">
      <div className="label text-accent">House style</div>
      <ul className="space-y-2.5 text-[13px] leading-relaxed text-ink-300">
        <li><span className="text-ink-50">Ask it like a person would.</span> One or two plain sentences.</li>
        <li><span className="text-ink-50">Don&apos;t repeat directions.</span> The line under the question already says how to answer.</li>
        <li><span className="text-ink-50">Explain the idea, not the lines.</span> Main idea, a strategy that carries over, the usual mistake, a pattern to reuse.</li>
      </ul>
      <div className="border-t border-ink-800 pt-3" aria-live="polite">
        {notes === null ? (
          <p className="font-mono text-[11px] text-ink-500">Checks run as you type.</p>
        ) : notes.length === 0 ? (
          <p className="flex items-center gap-2 font-mono text-[12px] text-accent" data-testid="style-ok"><span className="h-1.5 w-1.5 bg-accent" /> Reads well.</p>
        ) : (
          <ul className="space-y-2" data-testid="style-notes">
            {notes.map((n) => (
              <li key={n} className="flex gap-2 text-[13px] text-signal-soft"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 bg-signal" />{n}</li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
