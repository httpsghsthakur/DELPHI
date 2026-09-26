/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        delphi: {
          dark: '#0A0F1C',
          blue: '#1E3A8A',
          teal: '#0D9488',
          accent: '#38BDF8',
          card: '#111827',
          border: '#1F2937'
        }
      }
    },
  },
  plugins: [],
}
