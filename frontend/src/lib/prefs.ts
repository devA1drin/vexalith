/** Small, pure helpers for the learner's saved preferences. */
import type { AnswerLanguage, Language } from "@/lib/api";

/** The answer box hint in the learner's preferred language. The grader reads all three either way. */
export const ANSWER_PLACEHOLDER: Record<AnswerLanguage, { long: string; short: string }> = {
  en: { long: "Write your answer here. Casual words are fine.", short: "A sentence or two is enough." },
  fil: { long: "Isulat ang sagot mo rito. Puwede ang simpleng salita.", short: "Isa o dalawang pangungusap ay sapat na." },
  taglish: { long: "Isulat ang answer mo dito. Okay lang kahit casual.", short: "Isa or dalawang sentence lang, okay na." },
};

export const ANSWER_LANGUAGE_LABEL: Record<AnswerLanguage, string> = { en: "English", fil: "Filipino", taglish: "Taglish" };

/** First practice language: what's in the URL, else the last one used here, else the profile's first pick. */
export function pickLanguage(url: string | null, stored: string | null, preferred: Language[], all: readonly string[]): Language {
  for (const v of [url, stored, preferred[0]]) if (v && all.includes(v)) return v as Language;
  return "python";
}
