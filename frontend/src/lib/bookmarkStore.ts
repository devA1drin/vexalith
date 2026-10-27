"use client";

/** Which items the learner has saved, loaded once per page and kept in step across buttons. */
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";

const EVENT = "vexalith:bookmarks";
let keys: Set<string> | null = null;
let pending: Promise<Set<string>> | null = null;

function load(): Promise<Set<string>> {
  if (keys) return Promise.resolve(keys);
  if (!pending) {
    pending = api.bookmarkKeys()
      .then((r) => (keys = new Set(r.keys)))
      .catch(() => new Set<string>())
      .finally(() => { pending = null; });
  }
  return pending;
}

function announce() {
  window.dispatchEvent(new Event(EVENT));
}

/** Keep the shared set in step after a change made somewhere else (e.g. the Bookmarks page). */
export function markSaved(key: string, saved: boolean) {
  if (!keys) keys = new Set();
  if (saved) keys.add(key);
  else keys.delete(key);
  announce();
}

export function questionKey(id: number) {
  return `q:${id}`;
}
export function exerciseKey(slug: string) {
  return `x:${slug}`;
}

export function useBookmark(key: string | null) {
  const [saved, setSaved] = useState<boolean | null>(key && keys ? keys.has(key) : null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!key) return;
    const sync = () => setSaved(keys ? keys.has(key) : null);
    window.addEventListener(EVENT, sync);
    load().then(sync);
    return () => window.removeEventListener(EVENT, sync);
  }, [key]);

  const toggle = useCallback(async () => {
    if (!key || busy) return;
    const next = !saved;
    setBusy(true);
    setError(null);
    setSaved(next);
    try {
      await api.setBookmark(key, next);
      markSaved(key, next);
    } catch (e) {
      setSaved(!next);
      setError(e instanceof Error ? e.message : "Couldn't save that.");
    } finally {
      setBusy(false);
    }
  }, [key, saved, busy]);

  return { saved, busy, error, toggle };
}
