import type { CodeLanguage } from "./api";

/** How each language runs in the browser, shown on the exercise pages. All free, nothing runs on a server. */
export const CODE_LANGUAGES: Record<CodeLanguage, { name: string; short: string; engine: string; firstLoad: string; credit?: string }> = {
  python: { name: "Python", short: "PY", engine: "Pyodide (CPython in WebAssembly)", firstLoad: "about 5 MB the first time" },
  javascript: { name: "JavaScript", short: "JS", engine: "its built-in JavaScript engine, in a locked-down worker", firstLoad: "nothing to download" },
  cpp: { name: "C++", short: "C++", engine: "Clang compiled to WebAssembly (YoWASP)", firstLoad: "about 23 MB the first time" },
  java: {
    name: "Java",
    short: "JAVA",
    engine: "OpenJDK javac on CheerpJ",
    firstLoad: "about 20 MB the first time",
    credit: "Java runs on CheerpJ by Leaning Technologies, used free under its Community License.",
  },
  php: { name: "PHP", short: "PHP", engine: "php-wasm (PHP 8 in WebAssembly)", firstLoad: "about 3 MB the first time" },
};

export const CODE_LANGUAGE_ORDER: CodeLanguage[] = ["python", "javascript", "cpp", "java", "php"];
