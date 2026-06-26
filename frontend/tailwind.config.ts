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
        // Fondo cálido y superficies
        cream: {
          50: "#faf7f1",
          100: "#f4efe6",
          200: "#ece4d6",
          300: "#ddd0bb",
        },
        // Acento terracota
        clay: {
          400: "#d28b5e",
          500: "#c2703d",
          600: "#a85d30",
          700: "#8a4c28",
        },
        // Texto / tinta cálida
        ink: {
          900: "#2b2823",
          700: "#4a453d",
          500: "#8b8278",
          400: "#a89f93",
        },
        line: "#e8e0d2",
      },
      fontFamily: {
        serif: ["var(--font-fraunces)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(43, 40, 35, 0.04), 0 4px 16px rgba(43, 40, 35, 0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
