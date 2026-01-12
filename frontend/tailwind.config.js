/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sprout: {
          50: '#f6fdf6',
          100: '#e3f9e3',
          200: '#c6efc6',
          300: '#9ae09a',
          400: '#6ccb6c',
          500: '#4caf50',
          600: '#3d8b40',
          700: '#326d34',
          800: '#29562a',
          900: '#234823',
        },
      },
    },
  },
  plugins: [],
}
