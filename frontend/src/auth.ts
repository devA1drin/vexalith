/**
 * Auth.js (NextAuth v5) configuration.
 *
 * Providers are enabled only when their credentials exist, so the app builds
 * and runs with none configured (the login page then explains that sign-in
 * isn't configured yet).
 *   GitHub: AUTH_GITHUB_ID / AUTH_GITHUB_SECRET
 *   Google: AUTH_GOOGLE_ID / AUTH_GOOGLE_SECRET
 */
import NextAuth, { type NextAuthConfig } from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import type { Provider } from "next-auth/providers";

export type ProviderInfo = { id: "github" | "google"; name: string };

const providers: Provider[] = [];
export const availableProviders: ProviderInfo[] = [];

if (process.env.AUTH_GITHUB_ID && process.env.AUTH_GITHUB_SECRET) {
  providers.push(GitHub);
  availableProviders.push({ id: "github", name: "GitHub" });
}
if (process.env.AUTH_GOOGLE_ID && process.env.AUTH_GOOGLE_SECRET) {
  providers.push(Google);
  availableProviders.push({ id: "google", name: "Google" });
}

declare module "next-auth" {
  interface Session {
    provider?: string;
    providerAccountId?: string;
  }
}

export const authConfig = {
  providers,
  trustHost: true,
  session: { strategy: "jwt", maxAge: 30 * 24 * 60 * 60 },
  pages: { signIn: "/login", error: "/login" },
  callbacks: {
    jwt({ token, account, profile }) {
      // Persist the stable provider identity on first sign-in.
      if (account) {
        token.provider = account.provider;
        token.providerAccountId = account.providerAccountId;
        const p = profile as { avatar_url?: string; picture?: string } | undefined;
        token.picture = token.picture ?? p?.avatar_url ?? p?.picture ?? null;
      }
      return token;
    },
    session({ session, token }) {
      session.provider = token.provider as string | undefined;
      session.providerAccountId = token.providerAccountId as string | undefined;
      return session;
    },
  },
} satisfies NextAuthConfig;

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
