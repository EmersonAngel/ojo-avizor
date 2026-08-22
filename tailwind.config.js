/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      // Lora, autoalojada en static/fonts/ (ver @font-face en entrada.css) —
      // nunca desde un CDN en vivo (docs/identidad-visual.md, apartados 3 y 8).
      fontFamily: {
        display: ['Lora', 'ui-serif', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
