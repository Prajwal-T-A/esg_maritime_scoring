/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'esg-green': '#10b981',
        'esg-orange': '#f59e0b',
        'esg-red': '#ef4444',
      },
    },
  },
  plugins: [],
}
