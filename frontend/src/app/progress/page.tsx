"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError, type ProgressOut } from "@/lib/api";
import { MasteryChart } from "@/components/MasteryChart";
import { CountUp } from "@/components/CountUp";

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.progress().then(setData).catch((e) => {
      if (e instanceof ApiError && e.status === 401) window.location.href = "/login?callbackUrl=/progress";
      else setError(e instanceof Error ? e.message : "Failed");
    });
  }, []);

  const weakest = data?.domains.length ? [...data.domains].sort((a, b) => a.mastery - b.mastery)[0] : null;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">02 · Progress{data && ` · ${data.display_name}`}</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Where your logic holds.</h1>
        </div>
        <Link href="/practice" className="btn-primary">Continue <span className="btn-arrow">→</span></Link>
      </div>
      {error && <p role="alert" className="border-l-2 border-signal pl-3 text-sm text-signal-soft">{error}</p>}
      {!data && !error && <div className="card h-48 animate-pulse" />}
      {data && (
        <>
          <div className="grid grid-cols-2 border-l border-t border-ink-700 sm:grid-cols-4">
            <Stat label="Answers" value={data.total_responses} i={0} />
            <Stat label="Skips" value={data.total_skips} i={1} />
            <Stat label="Avg mastery" value={Math.round(data.average_mastery * 100)} suffix="%" i={2} />
            <div className="rise border-b border-r border-ink-700 p-5" style={{ ["--rd" as string]: "240ms" }}>
              <div className="label">Focus next</div>
              <div className="mt-2 truncate font-display text-lg font-semibold text-accent">{weakest?.domain_name ?? "—"}</div>
            </div>
          </div>
          <MasteryChart domains={data.domains} />
          <div className="card overflow-x-auto">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">Mastery and attempts per skill</caption>
              <thead>
                <tr className="border-b border-ink-700">
                  <th className="label px-5 py-3 font-normal">Skill</th>
                  <th className="label px-5 py-3 text-right font-normal">Mastery</th>
                  <th className="label px-5 py-3 text-right font-normal">Attempts</th>
                </tr>
              </thead>
              <tbody>
                {data.domains.map((d) => (
                  <tr key={d.domain_slug} className="border-b border-ink-800 last:border-0">
                    <td className="px-5 py-3 text-ink-100">{d.domain_name}</td>
                    <td className="px-5 py-3 text-right font-mono text-ink-50">{Math.round(d.mastery * 100)}</td>
                    <td className="px-5 py-3 text-right font-mono text-ink-300">{d.attempts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, suffix = "", i }: { label: string; value: number; suffix?: string; i: number }) {
  return (
    <div className="rise border-b border-r border-ink-700 p-5" style={{ ["--rd" as string]: `${i * 80}ms` }}>
      <div className="label">{label}</div>
      <div className="mt-2 font-display text-4xl font-bold text-ink-50"><CountUp to={value} delay={i * 80} />{suffix}</div>
    </div>
  );
}
