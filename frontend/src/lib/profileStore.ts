"use client";

/**
 * The signed-in learner's profile, fetched once per page load and shared by the header menu,
 * the practice pages and the profile page. Saving the profile updates everyone.
 */
import { useEffect, useState } from "react";
import { api, type AnswerLanguage, type Profile } from "@/lib/api";
export { ANSWER_PLACEHOLDER, ANSWER_LANGUAGE_LABEL, pickLanguage } from "@/lib/prefs";

const EVENT = "vexalith:profile";
let cached: Profile | null = null;
let pending: Promise<Profile | null> | null = null;

export function loadProfile(): Promise<Profile | null> {
  if (cached) return Promise.resolve(cached);
  if (!pending) {
    pending = api.profile().then((p) => (cached = p)).catch(() => null).finally(() => { pending = null; });
  }
  return pending;
}

export function setProfile(p: Profile) {
  cached = p;
  window.dispatchEvent(new CustomEvent<Profile>(EVENT, { detail: p }));
}

/** Fetch again (after a change made through another endpoint) and tell everyone. */
export async function refreshProfile() {
  cached = null;
  const p = await loadProfile();
  if (p) setProfile(p);
}

export function useProfile(): Profile | null {
  const [p, setP] = useState<Profile | null>(cached);
  useEffect(() => {
    const on = (e: Event) => setP((e as CustomEvent<Profile>).detail);
    window.addEventListener(EVENT, on);
    loadProfile().then((v) => v && setP(v));
    return () => window.removeEventListener(EVENT, on);
  }, []);
  return p;
}

export function useAnswerLanguage(): AnswerLanguage {
  return useProfile()?.answer_language ?? "en";
}
