"use client";

import type { FeedbackPayload } from "@/lib/api";

export function FeedbackCard({ feedback }: { feedback: FeedbackPayload }) {
  const pct = Math.round(feedback.overall_score * 100);
  return (
    <div className="space-y-4 rounded-xl border border-ink-700 bg-ink-900/60 p-5 shadow-lg">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-ink-50">Feedback</h3>
          <p className="text-xs text-ink-400">
            Provider: <code className="text-accent-soft">{feedback.provider_used}</code>
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-accent">{pct}%</div>
          <div className="text-xs uppercase tracking-wide text-ink-400">Overall</div>
        </div>
      </div>

      {feedback.raw_explanation && (
        <p className="text-sm text-ink-200 leading-relaxed">{feedback.raw_explanation}</p>
      )}

      {Object.keys(feedback.domain_scores).length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-medium text-ink-300">Domain scores</h4>
          <ul className="flex flex-wrap gap-2">
            {Object.entries(feedback.domain_scores).map(([slug, score]) => (
              <li
                key={slug}
                className="rounded-full bg-ink-800 px-3 py-1 text-xs text-ink-100"
              >
                {slug.replace(/_/g, " ")}:{" "}
                <span className="font-semibold text-accent-soft">
                  {Math.round(score * 100)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback.fallacies.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-medium text-rose-300">Detected fallacies</h4>
          <ul className="space-y-2">
            {feedback.fallacies.map((f, i) => (
              <li
                key={`${f.name}-${i}`}
                className="rounded-lg border border-rose-900/50 bg-rose-950/30 p-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-rose-200">
                    {f.name.replace(/_/g, " ")}
                  </span>
                  <span className="text-xs text-rose-400">
                    {Math.round(f.confidence * 100)}% conf.
                  </span>
                </div>
                <p className="mt-1 text-sm text-ink-200">{f.explanation}</p>
                {f.evidence_span && (
                  <p className="mt-1 text-xs italic text-ink-400">
                    Evidence: “{f.evidence_span}”
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback.reasoning_gaps.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-medium text-amber-200">Reasoning gaps</h4>
          <ul className="space-y-2">
            {feedback.reasoning_gaps.map((g, i) => (
              <li key={i} className="rounded-lg border border-amber-900/40 bg-amber-950/20 p-3">
                <p className="text-sm text-ink-100">{g.description}</p>
                <p className="mt-1 text-xs text-amber-200/80">
                  Improve: {g.how_to_improve}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {feedback.suggestions.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-medium text-ink-300">Suggestions</h4>
          <ul className="list-disc space-y-1 pl-5 text-sm text-ink-200">
            {feedback.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
