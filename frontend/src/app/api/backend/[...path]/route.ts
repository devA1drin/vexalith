/**
 * Same-origin proxy from the browser to the Vexalith API.
 * Only allow-listed routes are forwarded; authenticated routes get a freshly
 * minted backend JWT. Responses are never cached.
 */
import { NextResponse, type NextRequest } from "next/server";
import { auth } from "@/auth";
import { backendUrl, mintBackendToken } from "@/lib/backend";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

type Rule = { method: "GET" | "POST"; pattern: RegExp; public?: boolean };

const RULES: Rule[] = [
  { method: "GET", pattern: /^me$/ },
  { method: "GET", pattern: /^questions\/next$/ },
  { method: "GET", pattern: /^questions\/\d+$/ },
  { method: "POST", pattern: /^questions\/\d+\/skip$/ },
  { method: "GET", pattern: /^questions\/\d+\/hints$/ },
  { method: "POST", pattern: /^questions\/\d+\/hints$/ },
  { method: "POST", pattern: /^responses$/ },
  { method: "GET", pattern: /^progress$/ },
  { method: "GET", pattern: /^recommendations$/ },
  { method: "GET", pattern: /^daily$/, public: true },
  { method: "GET", pattern: /^daily\/me$/ },
  { method: "POST", pattern: /^feedback$/ },
  { method: "GET", pattern: /^feedback\/mine$/ },
  { method: "GET", pattern: /^feedback\/recent$/, public: true },
  { method: "GET", pattern: /^(languages|domains|health)$/, public: true },
];

const NO_STORE = { "Cache-Control": "no-store" };

async function forward(req: NextRequest, path: string[]) {
  const joined = path.join("/");
  const rule = RULES.find((r) => r.method === req.method && r.pattern.test(joined));
  if (!rule) return NextResponse.json({ detail: "Not found" }, { status: 404, headers: NO_STORE });

  const headers: Record<string, string> = { Accept: "application/json" };
  if (!rule.public) {
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json({ detail: "Sign in required" }, { status: 401, headers: NO_STORE });
    }
    try {
      headers.Authorization = `Bearer ${await mintBackendToken(session)}`;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Auth error";
      return NextResponse.json({ detail: msg }, { status: 500, headers: NO_STORE });
    }
  }

  let body: string | undefined;
  if (req.method === "POST") {
    body = await req.text();
    if (body.length > 20_000) {
      return NextResponse.json({ detail: "Payload too large" }, { status: 413, headers: NO_STORE });
    }
    headers["Content-Type"] = "application/json";
  }

  const target = `${backendUrl()}/api/${joined}${req.nextUrl.search}`;
  try {
    const upstream = await fetch(target, { method: req.method, headers, body, cache: "no-store" });
    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json", ...NO_STORE },
    });
  } catch {
    return NextResponse.json({ detail: "Backend unavailable" }, { status: 502, headers: NO_STORE });
  }
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, (await ctx.params).path);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return forward(req, (await ctx.params).path);
}
