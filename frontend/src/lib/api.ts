/**
 * Browser client. All calls go to the same-origin proxy (/api/backend/*),
 * which attaches a short-lived backend JWT derived from the Auth.js session.
 */

export type Language = "python" | "javascript" | "php" | "html" | "css" | "general";
export const LANGUAGE_IDS: Language[] = ["python", "javascript", "php", "html", "css", "general"];

export type Finding = { name: string; explanation: string; evidence_span?: string | null; confidence: number };
export type ReasoningGap = { description: string; how_to_improve: string };

export type FeedbackPayload = {
  verdict: "correct" | "partially_correct" | "incorrect";
  correctness_score: number;
  reasoning_score: number;
  overall_score: number;
  strengths: string[];
  missed_concepts: string[];
  misconceptions: Finding[];
  reasoning_gaps: ReasoningGap[];
  suggestions: string[];
  domain_scores: Record<string, number>;
  reference_answer?: string | null;
  raw_explanation: string;
  provider_used: string;
};

export type Question = {
  id: number;
  domain_slug: string;
  domain_name: string;
  difficulty: string;
  language: Language;
  title: string;
  code: string;
  prompt: string;
};

export type ResponseOut = { id: number; question_id: number; answer_text: string; created_at: string; feedback: FeedbackPayload };
export type DomainProgress = { domain_slug: string; domain_name: string; mastery: number; attempts: number };
export type LanguageProgress = { language: string; attempts: number; average_score: number };
export type ProgressOut = {
  user_id: number;
  display_name: string;
  domains: DomainProgress[];
  languages?: LanguageProgress[];
  total_responses: number;
  total_skips: number;
  average_mastery: number;
};

export type FeedbackCategory = "bug" | "feature_request" | "question_content" | "other";
export type MyFeedback = { id: number; rating: number; category: FeedbackCategory; message: string; page_context: string | null; created_at: string };
export type PublicFeedback = {
  id: number;
  author_name: string;
  author_avatar_url: string | null;
  rating: number;
  category: FeedbackCategory;
  message: string;
  created_at: string;
};

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api/backend${path}`, {
    ...init,
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body;
    } catch {
      /* ignore */
    }
    if (Array.isArray(detail)) detail = detail.map((d) => d?.msg ?? JSON.stringify(d)).join("; ");
    throw new ApiError(typeof detail === "string" ? detail : JSON.stringify(detail), res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  nextQuestion: (language: Language, exclude: number[] = []) =>
    request<Question>(`/questions/next?language=${language}${exclude.length ? `&exclude=${exclude.join(",")}` : ""}`),
  skip: (questionId: number, language: Language) =>
    request<{ skipped_question_id: number; next_question: Question }>(`/questions/${questionId}/skip?language=${language}`, {
      method: "POST",
      body: "{}",
    }),
  submitResponse: (question_id: number, answer_text: string) =>
    request<ResponseOut>("/responses", { method: "POST", body: JSON.stringify({ question_id, answer_text }) }),
  progress: () => request<ProgressOut>("/progress"),
  submitFeedback: (body: { rating: number; category: FeedbackCategory; message: string; page_context?: string | null }) =>
    request<MyFeedback>("/feedback", { method: "POST", body: JSON.stringify(body) }),
  myFeedback: () => request<MyFeedback[]>("/feedback/mine"),
  recentFeedback: () => request<PublicFeedback[]>("/feedback/recent"),
};
