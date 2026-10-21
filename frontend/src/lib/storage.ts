/** Persist the active learner id in localStorage for demo convenience. */

const KEY = "ct_user";

export type StoredUser = { id: number; display_name: string };

export function loadUser(): StoredUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as StoredUser) : null;
  } catch {
    return null;
  }
}

export function saveUser(user: StoredUser): void {
  localStorage.setItem(KEY, JSON.stringify(user));
}

export function clearUser(): void {
  localStorage.removeItem(KEY);
}
