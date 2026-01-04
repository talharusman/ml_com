/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#dc143c',
        secondary: '#1a1a1a',
        accent: '#ff6b35',
        'bg-dark': '#0f0f0f',
        'bg-light': '#f5f5f5',
        success: '#28a745',
      },
    },
  },
  plugins: [],
}
