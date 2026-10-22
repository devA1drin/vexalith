import type { Metadata, Viewport } from "next";
import { JetBrains_Mono, Space_Grotesk } from "next/font/google";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SITE } from "@/lib/site";
import "./globals.css";

const display = Space_Grotesk({ subsets: ["latin"], variable: "--font-display", display: "swap", weight: ["400", "500", "600", "700"] });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(SITE.url),
  title: { default: `${SITE.name} — ${SITE.tagline}`, template: `%s | ${SITE.name}` },
  description: SITE.description,
  applicationName: SITE.name,
  keywords: ["programming", "code reasoning", "debugging", "Big-O", "code review", "code tracing", "Python", "JavaScript", "PHP", "HTML", "CSS", "algorithms", "logic puzzles"],
  openGraph: { type: "website", siteName: SITE.name, title: `${SITE.name} — ${SITE.tagline}`, description: SITE.description, url: SITE.url },
  twitter: { card: "summary_large_image", title: `${SITE.name} — ${SITE.tagline}`, description: SITE.description },
  icons: { icon: [{ url: "/icon.svg", type: "image/svg+xml" }, { url: "/favicon.ico", sizes: "any" }] },
};

export const viewport: Viewport = { themeColor: "#0c0d0c" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${mono.variable}`} style={{ ["--font-sans" as string]: "var(--font-display)" }}>
      <body className="flex min-h-screen flex-col">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:bg-accent focus:px-3 focus:py-2 focus:text-ink-950">Skip to content</a>
        <Nav />
        <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-10 sm:px-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
