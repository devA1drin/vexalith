/** Small form pieces shared by the admin pages. */
export function AdminSelect({ label, value, onChange, options, all = "All" }: {
  label: string; value: string; onChange: (v: string) => void; options: [string, string][]; all?: string | null;
}) {
  return (
    <label className="flex min-w-0 flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">{label}</span>
      <select
        className={`input w-full min-w-0 py-1.5 text-[13px] ${value ? "border-accent text-ink-50" : ""}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        data-testid={`admin-filter-${label.toLowerCase().replace(/\s+/g, "-")}`}
      >
        {all !== null && <option value="">{all}</option>}
        {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </label>
  );
}

export function Pips({ level }: { level: string }) {
  const n = { beginner: 1, intermediate: 2, advanced: 3 }[level] ?? 0;
  return (
    <span className="inline-flex items-center gap-1" title={level} aria-label={level}>
      {[1, 2, 3].map((i) => <i key={i} className={`inline-block h-2 w-2 ${i <= n ? "bg-accent" : "bg-ink-700"}`} />)}
    </span>
  );
}
