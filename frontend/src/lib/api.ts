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
  /** A generated mark the author picked (shown instead of a photo). */
  author_avatar?: string | null;
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
export type BadgeGroup = "answers" | "streaks" | "languages" | "code" | "paths" | "review";
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
export type LeaderboardEntry = { rank: number; name: string; xp: number; level: number; level_name: string; is_you: boolean; avatar: string | null };
export type LeaderboardOut = {
  period: "week" | "all";
  entries: LeaderboardEntry[];
  you: { rank: number | null; xp: number; name: string; level: number; level_name: string; visibility: Visibility; in_top: boolean; avatar: string | null };
  ranked: number;
  week_start?: string;
  week_end?: string;
};
export type XpProfile = { visibility: Visibility; handle: string; shown_as: string | null; name_available: boolean; name: string | null };

export class ApiError extends Error {
  /** For form errors: the field the message is about. */
  constructor(message: string, public status: number, public field?: string) {
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

// ── Mistake review ──
export type ReviewStatus = "to_fix" | "check_again";
export type ReviewItem = {
  key: string;
  kind: "question" | "exercise";
  id: number | null;
  slug: string | null;
  title: string;
  language: string;
  topic: string;
  topic_name: string;
  difficulty: string;
  question_kind: "explain" | "fill_blank" | "code";
  status: ReviewStatus;
  reason: "wrong" | "partial" | "timeout" | "failed" | "helped";
  reason_label: string;
  times_wrong: number;
  last_wrong_at: string | null;
  fixed_at: string | null;
  due_at: string | null;
  last_answer: string;
  feedback: string;
  explanation: string;
  code: string;
  score: number | null;
  tests: [number, number] | null;
  paths: string[];
};
export type FilterOption = { value: string; label: string; count: number };
export type ReviewFilters = { topic?: string; language?: string; path?: string; difficulty?: string; kind?: "" | "question" | "exercise" };
export type ReviewOut = {
  items: ReviewItem[];
  coming_back: { key: string; title: string; fixed_at: string; due_at: string }[];
  counts: { to_fix: number; check_again: number; waiting: number; done: number; shown: number };
  fixes: number;
  filters: { topics: FilterOption[]; languages: FilterOption[]; paths: FilterOption[]; difficulties: FilterOption[] };
  rules: { fix_xp: number; confirm_days: number; second_look: number };
};

// ── Timed quiz ──
export type QuizScope = "topic" | "language" | "path" | "mixed";
export type QuizBrief = {
  id: number;
  scope: QuizScope;
  scope_value: string;
  scope_label: string;
  length: number;
  time_limit_s: number;
  instant: boolean;
  status: "active" | "finished";
  started_at: string;
  deadline_at: string;
  remaining_s: number;
};
export type QuizRules = { quiz_xp: number; grace_s: number; beat_score: number; beat_min: number };
export type QuizOptions = {
  scopes: Record<QuizScope, FilterOption[]>;
  lengths: number[];
  minutes: number[];
  active: QuizBrief | null;
  rules: QuizRules;
  /** The learner's saved quiz settings from their profile, if any. */
  defaults: QuizStartBody | null;
};
export type QuizSlot = { position: number; state: "open" | "answered" | "skipped"; verdict: FeedbackPayload["verdict"] | null };
export type QuizState = QuizBrief & {
  server_now: string;
  current: number | null;
  returning: boolean;
  question: Question | null;
  /** All questions in slot order (only while the quiz is running). */
  questions: (Question | null)[];
  slots: QuizSlot[];
  answered: number;
  feedback?: FeedbackPayload | null;
};
export type QuizReviewRow = {
  position: number;
  question_id: number;
  title: string;
  language: string;
  difficulty: string;
  topic_name: string;
  kind: "explain" | "fill_blank";
  code: string;
  prompt: string;
  answer: string;
  status: "correct" | "partial" | "wrong" | "unanswered" | "skipped";
  score: number;
  feedback: string;
  reference_answer: string;
  accepted_answers: string[];
  key_idea: string;
};
export type QuizResults = QuizBrief & {
  finished_at: string;
  ended_by: "done" | "time" | "ended";
  correct: number;
  score: number;
  time_used_s: number;
  xp: number;
  to_review: number;
  best_before: number | null;
  new_best: boolean;
  beat_the_clock: boolean;
  questions: QuizReviewRow[];
};
export type QuizHistory = {
  quizzes: {
    id: number;
    scope: QuizScope;
    scope_value: string;
    scope_label: string;
    length: number;
    correct: number;
    score: number;
    instant: boolean;
    time_limit_s: number;
    time_used_s: number;
    ended_by: string;
    finished_at: string;
  }[];
  best: { scope: QuizScope; scope_value: string; scope_label: string; best_score: number; best_correct: number; best_length: number; attempts: number; last_at: string }[];
  total: number;
};
export type QuizStartBody = { scope: QuizScope; value: string; length: number; minutes: number; instant: boolean };

// ── Profile ──
export type AnswerLanguage = "en" | "fil" | "taglish";
export type Profile = {
  display_name: string;
  sign_in_name: string;
  shown_name: string;
  avatar: string;
  avatars: string[];
  photo_url: string | null;
  leaderboard_avatar: string | null;
  bio: string;
  practice_languages: Language[];
  answer_language: AnswerLanguage;
  quiz_defaults: QuizStartBody | null;
  handle: string;
  visibility: Visibility;
  leaderboard_name: string | null;
  provider: string;
  /** Only true for accounts listed in the backend's ADMIN_IDENTITIES. */
  is_admin?: boolean;
  joined_at: string | null;
  limits: { name: [number, number]; handle: [number, number]; bio: number };
};
export type ProfileUpdate = Partial<{
  display_name: string;
  handle: string;
  visibility: Visibility;
  avatar: string;
  bio: string;
  practice_languages: Language[];
  answer_language: AnswerLanguage;
  quiz_defaults: QuizStartBody | null;
}>;
export type HandleCheck = { handle: string; available: boolean; reason: string };
export type ProfileSummary = LevelInfo & {
  badges_earned: number;
  badges_total: number;
  paths: { slug: string; name: string; mark: string; steps_done: number; steps_total: number; progress: number; started: boolean; finished: boolean }[];
  paths_finished: number;
  bookmarks: number;
  joined_at: string | null;
};

// ── Bookmarks ──
export type BookmarkKind = "question" | "exercise";
export type Bookmark = {
  key: string;
  kind: BookmarkKind;
  id: number | null;
  slug: string | null;
  title: string;
  language: string;
  topic: string;
  topic_name: string;
  difficulty: string;
  question_kind: "explain" | "fill_blank" | "code";
  note: string;
  saved_at: string;
  result: "right" | "partial" | "wrong" | "solved" | "failed" | "new";
};
export type BookmarkFilters = { kind?: "" | BookmarkKind; topic?: string; language?: string };
export type BookmarksOut = {
  items: Bookmark[];
  counts: { total: number; questions: number; exercises: number; shown: number };
  filters: { topics: FilterOption[]; languages: FilterOption[] };
  limits: { note: number; max: number };
};
export type BookmarkSaved = { key: string; saved: boolean; note: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api/backend${path}`, {
    ...init,
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    let field: string | undefined;
    try {
      const body = await res.json();
      detail = body.detail ?? body;
      if (typeof body.field === "string") field = body.field;
    } catch {
      /* ignore */
    }
    if (Array.isArray(detail)) detail = detail.map((d) => d?.msg ?? JSON.stringify(d)).join("; ");
    throw new ApiError(typeof detail === "string" ? detail : JSON.stringify(detail), res.status, field);
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
  review: (f: ReviewFilters = {}) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(f)) if (v) q.set(k, v);
    const qs = q.toString();
    return request<ReviewOut>(`/review${qs ? `?${qs}` : ""}`);
  },
  retryQuestion: (id: number) => request<{ ok: boolean }>(`/review/questions/${id}/retry`, { method: "POST", body: "{}" }),
  retryExercise: (slug: string) => request<{ ok: boolean }>(`/review/exercises/${encodeURIComponent(slug)}/retry`, { method: "POST", body: "{}" }),
  quizOptions: () => request<QuizOptions>("/quiz/options"),
  profile: () => request<Profile>("/profile"),
  saveProfile: (body: ProfileUpdate) => request<Profile>("/profile", { method: "PUT", body: JSON.stringify(body) }),
  checkHandle: (handle: string) => request<HandleCheck>(`/profile/handle?${new URLSearchParams({ handle })}`),
  profileSummary: () => request<ProfileSummary>("/profile/summary"),
  bookmarks: (f: BookmarkFilters = {}) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(f)) if (v) q.set(k, v);
    const qs = q.toString();
    return request<BookmarksOut>(`/bookmarks${qs ? `?${qs}` : ""}`);
  },
  bookmarkKeys: () => request<{ keys: string[] }>("/bookmarks/keys"),
  /** ``key`` is "q:<id>" or "x:<slug>". Leave ``note`` out to keep the current one. */
  setBookmark: (key: string, saved: boolean, note?: string) =>
    request<BookmarkSaved>(
      key.startsWith("q:") ? `/bookmarks/questions/${Number(key.slice(2))}` : `/bookmarks/exercises/${encodeURIComponent(key.slice(2))}`,
      { method: "PUT", body: JSON.stringify(note === undefined ? { saved } : { saved, note }) },
    ),
  quizHistory: () => request<QuizHistory>("/quiz/history"),
  startQuiz: (body: QuizStartBody) => request<QuizState>("/quiz", { method: "POST", body: JSON.stringify(body) }),
  quiz: (id: number) => request<QuizState>(`/quiz/${id}`),
  quizAnswer: (id: number, position: number, answer_text: string) =>
    request<QuizState>(`/quiz/${id}/answer`, { method: "POST", body: JSON.stringify({ position, answer_text }) }),
  quizSkip: (id: number, position: number) => request<QuizState>(`/quiz/${id}/skip`, { method: "POST", body: JSON.stringify({ position }) }),
  finishQuiz: (id: number) => request<QuizResults>(`/quiz/${id}/finish`, { method: "POST", body: "{}" }),
  quizResults: (id: number) => request<QuizResults>(`/quiz/${id}/results`),
  revealSolution: (slug: string, confirm: boolean) =>
    request<ExerciseHelp>(`/exercises/${encodeURIComponent(slug)}/solution`, { method: "POST", body: JSON.stringify({ confirm }) }),
};
