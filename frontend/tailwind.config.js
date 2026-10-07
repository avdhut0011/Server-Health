/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        noc: {
          bg: "#0b0f17",
          card: "#131b2e",
          border: "#1e293b",
          healthy: "#10b981",
          warning: "#f59e0b",
          critical: "#ef4444",
          down: "#64748b",
          info: "#38bdf8"
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      }
    },
  },
  plugins: [],
}
