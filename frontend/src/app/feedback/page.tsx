import type { Metadata } from "next";
import { auth, availableProviders } from "@/auth";
import { FeedbackClient } from "./FeedbackClient";

export const metadata: Metadata = { title: "Feedback" };

export default async function FeedbackPage() {
  const session = await auth();
  return (
    <div className="space-y-8">
      <div className="border-b border-ink-700 pb-5">
        <p className="label mb-2">03 · Feedback</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-50">Found a bug in our logic?</h1>
        <p className="mt-2 max-w-xl text-ink-300">Report a broken question, a wrong grade, or the feature you want next. Recent notes are public — emails never are.</p>
      </div>
      <FeedbackClient signedIn={!!session?.user} providers={availableProviders.map((p) => p.name)} />
    </div>
  );
}
