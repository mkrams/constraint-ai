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
        background: "#0a0a0f",
        foreground: "#e0e0e8",
        accent: "#6c5ce7",
        success: "#00b894",
        error: "#e74c3c",
        warning: "#f39c12",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Courier New"', "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
