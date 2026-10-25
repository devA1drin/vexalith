"use client";

import { useRef } from "react";

/** A plain, dependable code box: monospace, line numbers, Tab indents, Ctrl/Cmd+Enter runs. */
export function CodeEditor({
  value,
  onChange,
  onRun,
  indent = "    ",
  label,
}: {
  value: string;
  onChange: (v: string) => void;
  onRun?: () => void;
  indent?: string;
  label: string;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const gutter = useRef<HTMLDivElement>(null);
  const lines = value.split("\n").length;

  const edit = (next: string, caret: number) => {
    onChange(next);
    requestAnimationFrame(() => ref.current?.setSelectionRange(caret, caret));
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const t = e.currentTarget;
    const { selectionStart: a, selectionEnd: b } = t;
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onRun?.();
      return;
    }
    if (e.key === "Tab" && !e.shiftKey && a === b) {
      e.preventDefault();
      edit(value.slice(0, a) + indent + value.slice(b), a + indent.length);
      return;
    }
    if (e.key === "Enter" && a === b) {
      // keep the current line's indentation, plus one level after ':' or '{'
      const lineStart = value.lastIndexOf("\n", a - 1) + 1;
      const current = value.slice(lineStart, a);
      let pad = current.match(/^\s*/)?.[0] ?? "";
      if (/[:{]\s*$/.test(current)) pad += indent;
      e.preventDefault();
      edit(value.slice(0, a) + "\n" + pad + value.slice(b), a + 1 + pad.length);
    }
  };

  return (
    <div className="flex border border-ink-700 bg-ink-950 focus-within:border-accent">
      <div
        ref={gutter}
        aria-hidden="true"
        className="select-none overflow-hidden border-r border-ink-800 py-3 pl-2 pr-2 text-right font-mono text-[13px] leading-6 text-ink-600"
      >
        {Array.from({ length: lines }, (_, i) => (
          <div key={i}>{i + 1}</div>
        ))}
      </div>
      <textarea
        ref={ref}
        aria-label={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        onScroll={(e) => {
          if (gutter.current) gutter.current.scrollTop = e.currentTarget.scrollTop;
        }}
        spellCheck={false}
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
        wrap="off"
        rows={Math.min(Math.max(lines + 2, 10), 24)}
        className="min-w-0 flex-1 resize-y overflow-auto bg-transparent px-3 py-3 font-mono text-[13px] leading-6 text-ink-50 outline-none"
        data-testid="code-editor"
      />
    </div>
  );
}
