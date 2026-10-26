import type { LevelInfo } from "@/lib/api";
import { LevelMark } from "@/components/BadgeMark";

/** Level, name and the bar to the next level. */
export function LevelCard({ info, week, compact = false }: { info: LevelInfo; week?: number; compact?: boolean }) {
  const pct = Math.round(info.progress * 100);
  return (
    <div className={`card flex items-center gap-4 ${compact ? "p-4" : "p-5 sm:p-6"}`} data-testid="level-card">
      <LevelMark level={info.level} size={compact ? 48 : 68} />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <p className={`font-display font-bold text-ink-50 ${compact ? "text-xl" : "text-2xl sm:text-3xl"}`}>
            Level {info.level} <span className="text-accent">{info.level_name}</span>
          </p>
          <p className="font-mono text-[12px] text-ink-300">
            <span className="text-ink-50">{info.xp.toLocaleString()}</span> XP
            {typeof week === "number" && <span className="text-ink-400"> · {week.toLocaleString()} this week</span>}
          </p>
        </div>
        <div
          className="mt-3 h-2 border border-ink-600 bg-ink-950"
          role="progressbar"
          aria-valuemin={info.level_floor}
          aria-valuemax={info.next_level_at}
          aria-valuenow={info.xp}
          aria-label={`XP to level ${info.level + 1}`}
        >
          <div className="bar-grow h-full bg-accent" style={{ width: `${Math.max(2, pct)}%` }} />
        </div>
        <p className="mt-2 font-mono text-[11px] text-ink-400">
          {info.to_next.toLocaleString()} XP to level {info.level + 1}, {info.next_level_name}
        </p>
      </div>
    </div>
  );
}
