/**
 * Thin client for the FastAPI backend.
 * Base URL comes from NEXT_PUBLIC_API_URL (default localhost:8000).
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type FallacyFinding = {
  name: string;
  explanation: string;
  evidence_span?: string | null;
  confidence: number;
};

export type ReasoningGap = {
  description: string;
  how_to_improve: string;
};

export type FeedbackPayload = {
  fallacies: FallacyFinding[];
  reasoning_gaps: ReasoningGap[];
  domain_scores: Record<string, number>;
  suggestions: string[];
  overall_score: number;
  raw_explanation: string;
  provider_used: string;
};

export type User = {
  id: number;
  display_name: string;
  created_at: string;
};

export type Question = {
  id: number;
  domain_slug: string;
  domain_name: string;
  difficulty: string;
  title: string;
  scenario: string;
  prompt: string;
};

export type ResponseOut = {
  id: number;
  user_id: number;
  question_id: number;
  answer_text: string;
  created_at: string;
  feedback: FeedbackPayload;
};

export type DomainProgress = {
  domain_slug: string;
  domain_name: string;
  mastery: number;
  attempts: number;
};

export type ProgressOut = {
  user_id: number;
  display_name: string;
  domains: DomainProgress[];
  total_responses: number;
  average_mastery: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json() as Promise<T>;
}

export const api = {
  createUser: (display_name: string) =>
    request<User>("/api/users", {
      method: "POST",
      body: JSON.stringify({ display_name }),
    }),

  getUser: (id: number) => request<User>(`/api/users/${id}`),

  nextQuestion: (user_id: number) =>
    request<Question>(`/api/questions/next?user_id=${user_id}`),

  submitResponse: (user_id: number, question_id: number, answer_text: string) =>
    request<ResponseOut>("/api/responses", {
      method: "POST",
      body: JSON.stringify({ user_id, question_id, answer_text }),
    }),

  progress: (user_id: number) => request<ProgressOut>(`/api/progress/${user_id}`),

  health: () =>
    request<{
      status: string;
      llm_configured: boolean;
      hf_available: boolean;
      database: string;
      details: Record<string, unknown>;
    }>("/api/health"),
};

export { API_URL };
