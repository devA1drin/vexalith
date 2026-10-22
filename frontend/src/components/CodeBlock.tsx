"use client";

import type React from "react";
import { Highlight, type PrismTheme } from "prism-react-renderer";
import { Prism } from "@/lib/prism";

/** Graphite + lime syntax theme (keywords lime, strings warm, numbers orange). */
const theme: PrismTheme = {
  plain: { color: "#e4e3dd", backgroundColor: "transparent" },
  styles: [
    { types: ["comment", "prolog", "doctype", "cdata"], style: { color: "#7a7a73", fontStyle: "italic" } },
    { types: ["keyword", "builtin", "boolean", "important", "atrule"], style: { color: "#c8f031" } },
    { types: ["string", "char", "template-string", "attr-value"], style: { color: "#e8d6a3" } },
    { types: ["number", "constant"], style: { color: "#ff9a7a" } },
    { types: ["function", "class-name"], style: { color: "#f2f1ec", fontWeight: "600" } },
    { types: ["operator", "punctuation"], style: { color: "#a5a49d" } },
    { types: ["property", "variable", "parameter"], style: { color: "#d4d9c4" } },
    { types: ["tag"], style: { color: "#c8f031" } },
    { types: ["attr-name", "selector"], style: { color: "#f2f1ec" } },
    { types: ["delimiter"], style: { color: "#ff9a7a" } },
    { types: ["macro", "directive", "directive-hash"], style: { color: "#a9b98a" } },
  ],
};

/** The missing-code marker in fill-in-the-blank snippets. */
const BLANK = /(_{4,})/;

/** Render a token, swapping any ____ marker for a highlighted, labelled slot. */
function TokenSpan({ props }: { props: { children?: React.ReactNode; className?: string; style?: React.CSSProperties } }) {
  const text = typeof props.children === "string" ? props.children : null;
  if (!text || !BLANK.test(text)) return <span {...props} />;
  return (
    <span className={props.className} style={props.style}>
      {text.split(BLANK).map((part, i) =>
        BLANK.test(part) ? (
          <span key={i} className="code-blank" data-testid="code-blank" aria-label="missing code" title="Missing code: type it in your answer">
            ?
          </span>
        ) : (
          part
        ),
      )}
    </span>
  );
}

/** Question language → Prism grammar, header filename and label. */
const LANG_META: Record<string, { prism: string; file: string; label: string }> = {
  python: { prism: "python", file: "snippet.py", label: "python" },
  javascript: { prism: "javascript", file: "snippet.js", label: "javascript" },
  php: { prism: "php", file: "snippet.php", label: "php" },
  cpp: { prism: "cpp", file: "snippet.cpp", label: "c++" },
  html: { prism: "markup", file: "snippet.html", label: "html" },
  css: { prism: "css", file: "snippet.css", label: "css" },
  general: { prism: "plain", file: "problem.txt", label: "general" },
};

export function CodeBlock({ code, language, filename }: { code: string; language: string; filename?: string }) {
  const meta = LANG_META[language] ?? LANG_META.general;
  const name = filename ?? meta.file;
  return (
    <div className="border border-ink-700 bg-ink-950">
      <div className="flex items-center justify-between border-b border-ink-700 px-4 py-2">
        <span className="label">{name}</span>
        <span className="label text-accent">{meta.label}</span>
      </div>
      <Highlight prism={Prism} theme={theme} code={code.replace(/\n$/, "")} language={meta.prism}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={`${className} overflow-x-auto p-4 font-mono text-[13px] leading-6`} style={{ ...style, background: "transparent" }} data-testid="code-block">
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })} className="table-row">
                <span className="table-cell select-none pr-4 text-right text-ink-600">{i + 1}</span>
                <span className="table-cell">
                  {line.map((token, key) => <TokenSpan key={key} props={getTokenProps({ token })} />)}
                </span>
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    </div>
  );
}
