/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./public/index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1976d2",
        secondary: "#424242",
        accent: "#f50057"
      }
    }
  },
  plugins: []
}
