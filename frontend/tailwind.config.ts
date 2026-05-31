import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        faith: {
          gold: "#D4AF37",
          bronze: "#A87C11",
          amber: "#F5A623",
          slate: "#1E293B",
          charcoal: "#0F172A",
          cream: "#FDFBF7",
          crimson: "#8B0000"
        }
      },
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      }
    },
  },
  plugins: [],
};
export default config;
