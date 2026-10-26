"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type XpOut } from "@/lib/api";
import { LevelCard } from "@/components/XpBar";
import { BadgeMark } from "@/components/BadgeMark";

/** Level bar and the latest badges, on the progress page. */
export function ProgressLevel() {
  const [data, setData] = useState<XpOut | null>(null);
  useEffect(() => {
    api.xp().then(setData).catch(() => setData(null));
  }, []);
  if (!data) return null;
  const earned = data.badges
    .filter((b) => b.earned)
    .sort((a, b) => (b.earned_at ?? "").localeCompare(a.earned_at ?? ""))
    .slice(0, 6);
  return (
    <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]">
      <LevelCard info={data} week={data.xp_this_week} compact />
      <Link href="/badges" className="card flex items-center gap-3 p-4 transition-colors hover:border-accent" data-testid="progress-badges">
        {earned.length ? (
          <span className="flex -space-x-1">
            {earned.map((b) => <BadgeMark key={b.key} id={b.key} group={b.group} earned size={34} title={b.name} />)}
          </span>
        ) : (
          <BadgeMark id="first-correct" group="answers" earned={false} size={34} />
        )}
        <span className="font-mono text-[12px] text-ink-300">
          <span className="text-accent">{data.badges_earned}</span>/{data.badges.length} badges <span className="text-ink-500">→</span>
        </span>
      </Link>
    </div>
  );
}
