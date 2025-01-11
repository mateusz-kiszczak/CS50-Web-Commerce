/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './auctions/templates/auctions/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

// "build:css": "tailwindcss -i ./src/styles/tailwind.css -o ./auctions/static/auctions/styles.css"