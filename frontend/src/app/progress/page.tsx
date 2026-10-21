"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type ProgressOut } from "@/lib/api";
import { loadUser } from "@/lib/storage";
import { MasteryChart } from "@/components/MasteryChart";

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const u = loadUser();
    setUserId(u?.id ?? null);
    if (!u) return;
    api
      .progress(u.id)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"));
  }, []);

  if (userId == null) {
    return (
      <div className="rounded-xl border border-ink-700 bg-ink-900/50 p-8 text-center space-y-3">
        <p className="text-ink-300">Create a learner profile on the home page first.</p>
        <Link href="/" className="text-accent hover:underline">
          ← Home
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-ink-50">Progress</h1>
      {error && <p className="text-sm text-rose-300">{error}</p>}
      {!data && !error && <p className="text-ink-400">Loading…</p>}
      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Learner" value={data.display_name} />
            <Stat label="Responses" value={String(data.total_responses)} />
            <Stat
              label="Avg mastery"
              value={`${Math.round(data.average_mastery * 100)}%`}
            />
          </div>
          <MasteryChart domains={data.domains} />
          <div className="overflow-x-auto rounded-xl border border-ink-700">
            <table className="w-full text-left text-sm">
              <thead className="bg-ink-900 text-ink-400">
                <tr>
                  <th className="px-4 py-2 font-medium">Domain</th>
                  <th className="px-4 py-2 font-medium">Mastery</th>
                  <th className="px-4 py-2 font-medium">Attempts</th>
                </tr>
              </thead>
              <tbody>
                {data.domains.map((d) => (
                  <tr key={d.domain_slug} className="border-t border-ink-800">
                    <td className="px-4 py-2 text-ink-100">{d.domain_name}</td>
                    <td className="px-4 py-2 text-accent-soft">
                      {Math.round(d.mastery * 100)}%
                    </td>
                    <td className="px-4 py-2 text-ink-300">{d.attempts}</td>
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

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-ink-700 bg-ink-900/50 px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-ink-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-ink-50">{value}</div>
    </div>
  );
}
