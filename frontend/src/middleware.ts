import { NextResponse } from "next/server";
import { auth } from "@/auth";

const PROTECTED = ["/paths", "/practice", "/code", "/progress", "/badges", "/leaderboard"];
const LEGACY_HOSTS = new Set(["critical-thinking-app-rho.vercel.app"]);

export default auth((req) => {
  const { nextUrl } = req;
  const primary = process.env.PRIMARY_HOST;

  // Old domain keeps working by redirecting to the primary Vexalith domain.
  const host = req.headers.get("host") ?? "";
  if (primary && LEGACY_HOSTS.has(host) && host !== primary) {
    const url = new URL(nextUrl.pathname + nextUrl.search, `https://${primary}`);
    return NextResponse.redirect(url, 308);
  }

  const isProtected = PROTECTED.some((p) => nextUrl.pathname === p || nextUrl.pathname.startsWith(`${p}/`));
  if (isProtected && !req.auth) {
    const login = new URL("/login", nextUrl.origin);
    login.searchParams.set("callbackUrl", nextUrl.pathname + nextUrl.search);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
});

export const config = {
  // Run on pages, skip static assets and the Auth.js routes themselves.
  matcher: ["/((?!api/auth|_next/static|_next/image|favicon.ico|icon.svg|.*\\.(?:png|svg|ico|webp)$).*)"],
};
