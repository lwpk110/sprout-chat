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
      fontSize: {
        'sprout-base': ['18px', '1.5'],    // Body text - age appropriate
        'sprout-lg': ['24px', '1.4'],      // Titles
        'sprout-xl': ['28px', '1.3'],      // Main titles
        'sprout-sm': ['16px', '1.5'],      // Secondary text
      },
      minWidth: {
        '48': '12rem',  // Minimum touch target for children
      },
      minHeight: {
        '48': '12rem',  // Minimum touch target for children
      },
    },
  },
  plugins: [],
}
