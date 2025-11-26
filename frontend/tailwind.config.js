/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette for HITL app
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // Add more custom colors as needed
      },
      // Mobile-first breakpoints (Tailwind default is already mobile-first)
      screens: {
        'xs': '475px',
        // sm: '640px', // Already included
        // md: '768px', // Already included
        // lg: '1024px', // Already included
        // xl: '1280px', // Already included
        // 2xl: '1536px', // Already included
      },
      // Custom spacing for mobile optimization
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
}
