/**
 * Server-only helpers to call the Vexalith API on behalf of the signed-in user.
 *
 * The browser never talks to the backend with a user id. Instead, this server
 * code mints a short-lived HS256 JWT (5 min) from the Auth.js session, signed
 * with BACKEND_JWT_SECRET, and the backend derives the user from it.
 */
import "server-only";
import { SignJWT } from "jose";
import type { Session } from "next-auth";

export const JWT_ISSUER = "vexalith-web";
export const JWT_AUDIENCE = "vexalith-api";

export function backendUrl(): string {
  const url = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  return url.replace(/\/+$/, "");
}

export async function mintBackendToken(session: Session): Promise<string> {
  const secret = process.env.BACKEND_JWT_SECRET;
  if (!secret) throw new Error("BACKEND_JWT_SECRET is not configured");
  const provider = session.provider;
  const pid = session.providerAccountId;
  if (!provider || !pid) throw new Error("Session is missing provider identity");
  return new SignJWT({
    provider,
    provider_account_id: pid,
    name: session.user?.name ?? null,
    email: session.user?.email ?? null,
    picture: session.user?.image ?? null,
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setSubject(`${provider}:${pid}`)
    .setIssuer(JWT_ISSUER)
    .setAudience(JWT_AUDIENCE)
    .setIssuedAt()
    .setExpirationTime("5m")
    .sign(new TextEncoder().encode(secret));
}
