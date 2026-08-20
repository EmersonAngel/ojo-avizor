/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      // Serif de sistema, no descargada (docs/identidad-visual.md, apartado 8:
      // "tipografías descargadas de terceros encarecen la carga"). No hay
      // @font-face ni <link> a ninguna fuente externa en ningún lado.
      fontFamily: {
        display: ['ui-serif', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
