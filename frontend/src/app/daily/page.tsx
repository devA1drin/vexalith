import type { Metadata } from "next";
import Link from "next/link";
import { auth } from "@/auth";
import { DailyChallengeCard } from "@/components/DailyChallenge";

export const metadata: Metadata = {
  title: "Daily challenge",
  description: "One programming reasoning question a day, the same for everyone. Keep your streak going.",
};

export default async function DailyPage() {
  const session = await auth();
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-ink-700 pb-5">
        <div>
          <p className="label mb-2">Daily · one question, everyone</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Today&apos;s challenge.</h1>
        </div>
        {session?.user && <Link href="/progress" className="btn-ghost">Your progress <span className="btn-arrow">→</span></Link>}
      </div>
      <DailyChallengeCard signedIn={!!session?.user} full />
      <section className="grid gap-px border border-ink-700 bg-ink-700 sm:grid-cols-3" aria-label="How the daily challenge works">
        {[
          ["01", "Same for everyone", "Everyone gets the same question on the same day, so you can compare answers with friends."],
          ["02", "Resets at Manila midnight", "A new question appears at 00:00 Asia/Manila (UTC+8). The language changes every day, and the skill changes every week."],
          ["03", "Keep the streak", "Answer it on consecutive days to grow your streak. Missing a day resets it, but your best run is kept."],
        ].map(([n, h, p]) => (
          <div key={n} className="bg-ink-900 p-5">
            <div className="font-mono text-sm text-ink-500">{n}</div>
            <h2 className="mt-2 font-display text-lg font-semibold text-ink-50">{h}</h2>
            <p className="mt-1 text-sm text-ink-400">{p}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
