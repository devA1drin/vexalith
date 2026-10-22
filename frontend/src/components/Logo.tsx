/**
 * Vexalith mark: two logic paths start as separate inputs (open nodes, top),
 * step down like circuit traces and converge on one output node — a "V".
 */
export function LogoMark({ className = "h-7 w-7", framed = true }: { className?: string; framed?: boolean }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      {framed && <rect x="0.5" y="0.5" width="63" height="63" fill="#0c0d0c" stroke="#323331" />}
      <g fill="none" stroke="#c8f031" strokeWidth="5" strokeLinecap="square" strokeLinejoin="miter">
        <path d="M12 13v6l20 29" />
        <path d="M52 13v6L32 48" />
      </g>
      <rect x="8" y="7" width="8" height="8" fill="#0c0d0c" stroke="#c8f031" strokeWidth="3" />
      <rect x="48" y="7" width="8" height="8" fill="#0c0d0c" stroke="#c8f031" strokeWidth="3" />
      <rect x="28" y="44" width="8" height="8" fill="#c8f031" />
    </svg>
  );
}

export function Wordmark() {
  return (
    <span className="group flex items-center gap-2.5">
      <LogoMark className="h-7 w-7 transition-transform duration-300 group-hover:rotate-[-4deg]" />
      <span className="font-display text-[19px] font-bold tracking-tight text-ink-50">
        Vexalith<span className="text-accent">.</span>
      </span>
    </span>
  );
}
