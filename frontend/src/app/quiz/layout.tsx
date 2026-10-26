import type { Metadata } from "next";

export const metadata: Metadata = { title: "Timed quiz" };

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
