/** Browser client for the admin dashboard (through the same-origin proxy). */
import { ApiError } from "@/lib/api";
import { adminQuery } from "@/lib/adminFormat";

export type Bar = { key: string; label: string; attempts: number; accuracy: number | null };
export type HardQuestion = { id: number; title: string; topic: string; language: string; attempts: number; learners: number; pass_rate: number | null; fail_rate: number | null; rating: number };
export type Overview = {
  totals: {
    learners: number; new_7d: number; active_7d: number; active_30d: number; attempts: number; attempts_7d: number;
    accuracy: number | null; partial_rate: number | null; exercise_runs: number; exercise_solve_rate: number | null;
    feedback: number; feedback_unreviewed: number;
  };
  daily: { date: string; answers: number; runs: number; learners: number }[];
  by_topic: Bar[];
  by_language: Bar[];
  exercises_by_topic: Bar[];
  hardest: HardQuestion[];
  hardest_min_attempts: number;
};
export type Learner = {
  id: number; name: string; handle: string | null; confirm_word: string; board_name: string | null; visibility: string;
  email: string | null; provider: string; identity: string; avatar_url: string | null; avatar: string | null;
  xp: number; level: number; level_name: string; attempts: number; exercise_runs: number;
  last_active: string | null; joined: string | null; board_hidden: boolean; is_admin: boolean;
};
export type Page<T> = { items: T[]; total: number; page: number; pages: number };
export type LearnersOut = Page<Learner> & { total_all: number };
export type QuestionRow = {
  id: number; title: string; language: string; language_label: string; topic: string; topic_label: string;
  difficulty: string; kind: string; source: string; hidden: boolean; edited: boolean; preview: string;
  attempts?: number; learners?: number; pass_rate?: number | null; fail_rate?: number | null; partial?: number; rating?: number;
};
export type QuestionsOut = Page<QuestionRow> & { topics: { slug: string; name: string }[]; languages: { key: string; label: string }[] };
export type QuestionDetail = QuestionRow & {
  code: string; question_text: string; task_line: string; reference_answer: string; key_idea: string;
  hints: string[]; key_points: string[]; accepted_answers: string[]; edited_at: string | null;
};
export type SaveOut = { saved: boolean; notes: string[]; question?: QuestionDetail };
export type ExerciseRow = { slug: string; title: string; language: string; language_label: string; difficulty: string; topic: string; runs: number; learners: number; solvers: number; solve_rate: number | null; run_pass_rate: number | null };
export type FeedbackRow = {
  id: number; rating: number; category: string; message: string; page_context: string | null; created_at: string;
  author: { id: number; name: string; handle: string | null }; reviewed_at: string | null; hidden: boolean;
};
export type FeedbackOut = Page<FeedbackRow> & { categories: string[] };
export type AuditRow = { id: number; actor: string; action: string; target: string; details: Record<string, unknown>; created_at: string };
export type AuditOut = Page<AuditRow> & { actions: string[] };
export type NewQuestion = {
  topic: string; language: string; difficulty: string; title: string; code: string;
  question_text: string; key_points: string; reference_answer: string; key_idea: string; check_only?: boolean;
};

async function call<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api/backend/admin${path}`, {
    method: body === undefined ? "GET" : "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = typeof j.detail === "string" ? j.detail : Array.isArray(j.detail) ? j.detail.map((d: { msg?: string }) => d.msg).join("; ") : detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail || `Request failed (${res.status})`, res.status);
  }
  return res.json() as Promise<T>;
}

type Q = Record<string, string | number | undefined>;

export const adminApi = {
  overview: () => call<Overview>("/overview"),
  learners: (f: Q) => call<LearnersOut>(`/learners${adminQuery(f)}`),
  setBoard: (id: number, hidden: boolean) => call<Learner>(`/learners/${id}/board`, { hidden }),
  resetXp: (id: number, confirm: string) => call<Learner>(`/learners/${id}/reset-xp`, { confirm }),
  deleteLearner: (id: number, confirm: string) => call<{ deleted: boolean; removed: Record<string, number> }>(`/learners/${id}/delete`, { confirm }),
  questions: (f: Q) => call<QuestionsOut>(`/questions${adminQuery(f)}`),
  question: (id: number) => call<QuestionDetail>(`/questions/${id}`),
  saveQuestion: (id: number, body: { question_text?: string; reference_answer?: string; key_idea?: string; check_only?: boolean }) =>
    call<SaveOut>(`/questions/${id}`, body),
  setQuestionHidden: (id: number, hidden: boolean) => call<QuestionDetail>(`/questions/${id}/visibility`, { hidden }),
  createQuestion: (body: NewQuestion) => call<SaveOut>("/questions", body),
  styleCheck: (body: { question_text?: string; reference_answer?: string; key_idea?: string }) => call<{ notes: string[] }>("/style-check", body),
  exercises: () => call<{ items: ExerciseRow[] }>("/exercises"),
  feedback: (f: Q) => call<FeedbackOut>(`/feedback${adminQuery(f)}`),
  reviewFeedback: (id: number, reviewed: boolean) => call<unknown>(`/feedback/${id}/review`, { reviewed }),
  hideFeedback: (id: number, hidden: boolean) => call<unknown>(`/feedback/${id}/visibility`, { hidden }),
  deleteFeedback: (id: number) => call<unknown>(`/feedback/${id}/delete`, {}),
  audit: (f: Q) => call<AuditOut>(`/audit${adminQuery(f)}`),
};
