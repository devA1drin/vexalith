import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f7fb",
          100: "#e8eef6",
          200: "#cddceb",
          300: "#a0bfd9",
          400: "#6e9bc1",
          500: "#4d7ca7",
          600: "#3b628b",
          700: "#314f70",
          800: "#2b435e",
          900: "#273950",
          950: "#1a2534",
        },
        accent: {
          DEFAULT: "#e8a838",
          soft: "#f6d89a",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
