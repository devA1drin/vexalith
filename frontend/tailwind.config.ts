import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Graphite neutrals (warm-neutral, not blue-tinted)
        ink: {
          50: "#f2f1ec",
          100: "#e4e3dd",
          200: "#c9c8c1",
          300: "#a5a49d",
          400: "#85847f",
          500: "#66665f",
          600: "#4a4a46",
          700: "#323331",
          800: "#222322",
          900: "#161716",
          950: "#0c0d0c",
        },
        // One sharp accent: electric lime. "signal" is reserved for errors/limits.
        accent: { DEFAULT: "#c8f031", soft: "#dcf77a", dim: "#8fae17" },
        signal: { DEFAULT: "#ff5b2e", soft: "#ff9a7a" },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: { DEFAULT: "2px", md: "3px", lg: "4px", xl: "4px", "2xl": "4px" },
    },
  },
  plugins: [],
};

export default config;
