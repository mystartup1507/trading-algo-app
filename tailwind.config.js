/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        'neuromorph': ['"Orbitron"', 'monospace'],
        'digital': ['"Rajdhani"', 'sans-serif']
      }
    },
  },
  plugins: [],
}