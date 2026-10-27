/** Filter controls shared by Review mistakes and Bookmarks. */
import type { FilterOption } from "@/lib/api";

export function KindTabs({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const opts = [
    ["", "All"],
    ["question", "Questions"],
    ["exercise", "Code"],
  ];
  return (
    <div role="radiogroup" aria-label="Type" className="flex border border-ink-700">
      {opts.map(([v, l]) => (
        <button
          key={v}
          type="button"
          role="radio"
          aria-checked={value === v}
          onClick={() => onChange(v)}
          className={`px-3 py-1 font-mono text-[12px] uppercase tracking-wider ${value === v ? "bg-accent text-ink-950" : "text-ink-300 hover:text-ink-50"}`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}

export function Select({ label, value, options, onChange }: { label: string; value?: string; options: FilterOption[]; onChange: (v: string) => void }) {
  return (
    <label className="flex min-w-0 flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-wider text-ink-500">{label}</span>
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className={`input w-full min-w-0 py-1.5 text-[13px] ${value ? "border-accent text-ink-50" : ""}`}
        data-testid={`filter-${label.toLowerCase()}`}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label} ({o.count})
          </option>
        ))}
      </select>
    </label>
  );
}
