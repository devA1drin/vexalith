import { api, type XpSyncOut } from "@/lib/api";

/** Fired on window after XP is counted; the header chip and the toast listen for it. */
export const XP_EVENT = "vx:xp";

let inflight: Promise<XpSyncOut | null> | null = null;

/** Count anything new (answers, exercises, daily challenge) and tell the header and toast. Never throws. */
export function announceXp(): Promise<XpSyncOut | null> {
  if (inflight) return inflight;
  inflight = api
    .xpSync()
    .then((out) => {
      window.dispatchEvent(new CustomEvent<XpSyncOut>(XP_EVENT, { detail: out }));
      return out;
    })
    .catch(() => null)
    .finally(() => {
      inflight = null;
    });
  return inflight;
}
