/**
 * Browser client. All calls go to the same-origin proxy (/api/backend/*),
 * which attaches a short-lived backend JWT derived from the Auth.js session.
 */

export type Language = "python" | "javascript" | "php" | "cpp" | "java" | "html" | "css" | "general";
export const LANGUAGE_IDS: Language[] = ["python", "javascript", "php", "cpp", "java", "html", "css", "general"];

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
  key_points?: string[];
  accepted_answers?: string[];
  hints_used?: number;
  hint_penalty?: number;
  /** Language the learner wrote in: English, Filipino (Tagalog) or Taglish. */
  answer_language?: "en" | "fil" | "taglish";
  /** Short Filipino note shown when the answer was in Filipino / Taglish. */
  language_note?: string | null;
  /** True when this answer completed today's daily challenge. */
  daily_completed?: boolean;
  daily_streak?: number;
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
  /** "fill_blank": the snippet has a ____ blank and the learner supplies the missing code. */
  kind?: "explain" | "fill_blank";
  hint_count?: number;
  guide?: { look_for: string; good_answer?: string | null } | null;
};

export type HintsOut = { question_id: number; revealed: string[]; hint_count: number; penalty_per_hint: number; penalty: number };

export type ResponseOut = { id: number; question_id: number; answer_text: string; created_at: string; feedback: FeedbackPayload };
export type DomainProgress = { domain_slug: string; domain_name: string; mastery: number; attempts: number };
export type Focus = "fundamentals";
/** "adaptive" lets the Elo engine pick the level; the others pin it. */
export type Difficulty = "adaptive" | "beginner" | "intermediate" | "advanced";
export const DIFFICULTY_IDS: Difficulty[] = ["adaptive", "beginner", "intermediate", "advanced"];
export type PracticeOptions = { focus?: Focus | null; difficulty?: Difficulty; topic?: string | null };
export type TopicTip = { domain_slug: string; domain_name: string; mastery: number; attempts: number; suggested_difficulty: string; reason: string };
export type LanguageTip = { language: Language; name: string; attempts: number; average_score: number; reason: string };
export type RecommendationsOut = { language: Language; headline: string; topics: TopicTip[]; languages: LanguageTip[]; next_questions: Question[] };
export type FundamentalsStatus = {
  answers: number;
  strong_answers: number;
  recent_average: number;
  cleared: boolean;
  experienced: boolean;
  min_answers: number;
  pass_average: number;
};
export type LanguageProgress = { language: string; attempts: number; average_score: number; correct?: number; accuracy?: number };
export type ProgressDay = { date: string; answers: number; correct: number; average_score: number | null };
export type RecentAttempt = {
  question_id: number;
  title: string;
  language: Language;
  domain_name: string;
  difficulty: string;
  verdict: FeedbackPayload["verdict"];
  score: number;
  hints_used: number;
  created_at: string;
};
export type DailyOut = {
  date: string;
  timezone: string;
  resets_at: string;
  question_id: number;
  title: string;
  language: Language;
  domain_slug: string;
  domain_name: string;
  difficulty: string;
  kind: string;
};
export type DailyMeOut = DailyOut & {
  question: Question;
  completed: boolean;
  score: number | null;
  current_streak: number;
  best_streak: number;
  total_completed: number;
  last_days: { date: string; done: boolean; score: number | null }[];
};
export type ProgressOut = {
  user_id: number;
  display_name: string;
  domains: DomainProgress[];
  languages?: LanguageProgress[];
  fundamentals?: FundamentalsStatus | null;
  total_responses: number;
  total_skips: number;
  average_mastery: number;
  questions_answered?: number;
  questions_solved?: number;
  correct_answers?: number;
  accuracy?: number;
  average_score?: number;
  improvement?: number | null;
  hints_used?: number;
  history?: ProgressDay[];
  recent?: RecentAttempt[];
  current_streak?: number;
  best_streak?: number;
  daily_done_today?: boolean;
  daily_completed?: number;
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

export type CodeLanguage = "python" | "javascript" | "cpp" | "java" | "php";
export type ExerciseSummary = {
  slug: string;
  title: string;
  language: CodeLanguage;
  difficulty: "beginner" | "intermediate" | "advanced";
  topic: string;
  tests: number;
  best_passed: number;
  solved: boolean;
  attempted: boolean;
  solved_with_help?: boolean;
};
export type ExerciseList = { exercises: ExerciseSummary[]; runnable_languages: CodeLanguage[]; coming_soon: string[] };
/** "How to solve it": hints shown so far, and (once you pass or reveal it) the explanation and solution. */
export type ExerciseHelp = {
  hint_count: number;
  hints: string[];
  solution_revealed: boolean;
  solved_with_help: boolean;
  explanation: { idea: string; approach: string[]; pitfalls: string[]; pattern: string } | null;
  solution: string | null;
};
export type ExerciseDetail = Omit<ExerciseSummary, "tests"> & {
  help: ExerciseHelp;
  description: string;
  function: string;
  starter: string;
  signature: { params: string[]; returns: string } | null;
  timeout_ms: number;
  visible_tests: { args: unknown[]; expected: unknown }[];
  hidden_tests: { args: unknown[] }[];
};
export type SubmitCheck = { index: number; visible: boolean; passed: boolean; expected?: unknown };
export type SubmitOut = {
  slug: string;
  passed: number;
  total: number;
  solved: boolean;
  first_solve: boolean;
  checks: SubmitCheck[];
  message: string;
  help: ExerciseHelp;
};

export type LevelInfo = {
  xp: number;
  level: number;
  level_name: string;
  next_level_name: string;
  level_floor: number;
  next_level_at: number;
  to_next: number;
  /** 0..1 of the way from this level to the next. */
  progress: number;
};
export type BadgeGroup = "answers" | "streaks" | "languages" | "code" | "paths";
export type BadgeOut = { key: string; name: string; description: string; group: BadgeGroup; earned: boolean; earned_at: string | null };
export type XpOut = LevelInfo & {
  xp_this_week: number;
  badges: BadgeOut[];
  badges_earned: number;
  recent: { label: string; amount: number; kind: string; created_at: string }[];
};
/** What the learner hasn't been told about yet (shown once as a toast). */
export type XpNews = {
  xp: number;
  /** True when this counts work done before XP existed. */
  retro: boolean;
  items: { label: string; amount: number }[];
  badges: { key: string; name: string; description: string }[];
};
export type XpSyncOut = LevelInfo & { news: XpNews };
export type Visibility = "handle" | "name" | "anonymous" | "hidden";
export type LeaderboardEntry = { rank: number; name: string; xp: number; level: number; level_name: string; is_you: boolean };
export type LeaderboardOut = {
  period: "week" | "all";
  entries: LeaderboardEntry[];
  you: { rank: number | null; xp: number; name: string; level: number; level_name: string; visibility: Visibility; in_top: boolean };
  ranked: number;
  week_start?: string;
  week_end?: string;
};
export type XpProfile = { visibility: Visibility; handle: string; shown_as: string | null; name_available: boolean; name: string | null };

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

// ── Learning paths ──
export type StepStatus = "locked" | "open" | "done";
export type PathExercise = {
  title: string;
  any_language: boolean;
  options: { slug: string; language: string; language_name: string }[];
  passed: boolean;
  passed_slug: string | null;
};
export type PathStep = {
  number: number;
  key: string;
  title: string;
  blurb: string;
  levels: string;
  status: StepStatus;
  skipped: boolean;
  pool_size: number;
  target: number;
  answered: number;
  score: number;
  questions_passed: boolean;
  exercise: PathExercise | null;
  done_at: string | null;
};
export type PathSummary = {
  slug: string;
  name: string;
  blurb: string;
  mark: string;
  steps_total: number;
  steps_done: number;
  progress: number;
  started: boolean;
  finished: boolean;
  current_step: number;
  current_title: string;
  exercises: number;
};
export type PathRules = { pass_mark: number; step_xp: number; path_xp: number };
export type ContinueCard = { path: PathSummary; step: PathStep; from_history: boolean };
export type PathsOut = PathRules & { paths: PathSummary[]; continue: ContinueCard | null };
export type PathDetail = PathSummary & PathRules & { steps: PathStep[] };

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

function practiceQuery(language: Language, opts: PracticeOptions, exclude: number[] = []): string {
  const q = new URLSearchParams({ language });
  if (exclude.length) q.set("exclude", exclude.join(","));
  if (opts.focus) q.set("focus", opts.focus);
  if (opts.difficulty && opts.difficulty !== "adaptive") q.set("difficulty", opts.difficulty);
  if (opts.topic) q.set("topic", opts.topic);
  return q.toString();
}

export const api = {
  nextQuestion: (language: Language, exclude: number[] = [], opts: PracticeOptions = {}) =>
    request<Question>(`/questions/next?${practiceQuery(language, opts, exclude)}`),
  skip: (questionId: number, language: Language, opts: PracticeOptions = {}) =>
    request<{ skipped_question_id: number; next_question: Question }>(`/questions/${questionId}/skip?${practiceQuery(language, opts)}`, {
      method: "POST",
      body: "{}",
    }),
  question: (id: number) => request<Question>(`/questions/${id}`),
  recommendations: (language?: Language | null) =>
    request<RecommendationsOut>(`/recommendations${language ? `?language=${language}` : ""}`),
  submitResponse: (question_id: number, answer_text: string) =>
    request<ResponseOut>("/responses", { method: "POST", body: JSON.stringify({ question_id, answer_text }) }),
  progress: () => request<ProgressOut>("/progress"),
  daily: () => request<DailyOut>("/daily"),
  dailyMe: () => request<DailyMeOut>("/daily/me"),
  hints: (questionId: number) => request<HintsOut>(`/questions/${questionId}/hints`),
  revealHint: (questionId: number) => request<HintsOut>(`/questions/${questionId}/hints`, { method: "POST", body: "{}" }),
  submitFeedback: (body: { rating: number; category: FeedbackCategory; message: string; page_context?: string | null }) =>
    request<MyFeedback>("/feedback", { method: "POST", body: JSON.stringify(body) }),
  myFeedback: () => request<MyFeedback[]>("/feedback/mine"),
  recentFeedback: () => request<PublicFeedback[]>("/feedback/recent"),
  exercises: () => request<ExerciseList>("/exercises"),
  exercise: (slug: string) => request<ExerciseDetail>(`/exercises/${encodeURIComponent(slug)}`),
  submitExercise: (slug: string, code: string, results: { output: string | null; error: string | null }[]) =>
    request<SubmitOut>(`/exercises/${encodeURIComponent(slug)}/submit`, { method: "POST", body: JSON.stringify({ code, results }) }),
  exerciseHint: (slug: string) => request<ExerciseHelp>(`/exercises/${encodeURIComponent(slug)}/hints`, { method: "POST", body: "{}" }),
  xp: () => request<XpOut>("/xp"),
  paths: () => request<PathsOut>("/paths"),
  path: (slug: string) => request<PathDetail>(`/paths/${encodeURIComponent(slug)}`),
  pathQuestion: (slug: string, step: number, exclude: number[] = []) =>
    request<Question>(`/paths/${encodeURIComponent(slug)}/steps/${step}/next${exclude.length ? `?exclude=${exclude.join(",")}` : ""}`),
  skipAhead: (slug: string, step: number) =>
    request<PathDetail>(`/paths/${encodeURIComponent(slug)}/steps/${step}/skip-ahead`, { method: "POST", body: "{}" }),
  xpSync: () => request<XpSyncOut>("/xp/sync", { method: "POST", body: "{}" }),
  leaderboard: (period: "week" | "all") => request<LeaderboardOut>(`/leaderboard?period=${period}`),
  xpProfile: () => request<XpProfile>("/xp/profile"),
  setVisibility: (visibility: Visibility) => request<XpProfile>("/xp/profile", { method: "PUT", body: JSON.stringify({ visibility }) }),
  newHandle: () => request<XpProfile>("/xp/profile/handle", { method: "POST", body: "{}" }),
  revealSolution: (slug: string, confirm: boolean) =>
    request<ExerciseHelp>(`/exercises/${encodeURIComponent(slug)}/solution`, { method: "POST", body: JSON.stringify({ confirm }) }),
};
