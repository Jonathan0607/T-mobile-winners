/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'tmobile-magenta': '#E20074',
        'critical-red': '#D62828',
        'high-yellow': '#FFC300',
        'bg-dark': '#1A1A1A',
        'bg-card': '#2C2C2C',
        'text-muted': '#9CA3AF',
      },
    },
  },
  plugins: [],
}

