/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        delphi: {
          bg: '#0a0e17', // Main very dark background
          sidebar: '#0e1420', // Sidebar slightly lighter
          card: '#121a29', // Card background
          border: '#1e293b', // Card borders
          blue: '#1d4ed8', // Primary button blue
          blueHover: '#2563eb', // Button hover
          accent: '#38bdf8', // Cyan accents
          green: '#10b981', // Success/Positive
          orange: '#f59e0b', // Warning/Medium
          red: '#ef4444', // Danger/High
          text: '#f8fafc',
          textMuted: '#94a3b8'
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'globe': "url('/globe-bg.jpg')",
      }
    },
  },
  plugins: [],
}
