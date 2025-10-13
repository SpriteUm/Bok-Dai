module.exports = {
  content: ["./templates/**/*.{html,htm}"],
  theme: {
    extend: {
      colors: {
        'custom-green-lightest': '#E6E8E5',
        'custom-green-dull-green': '#C2D3C2',
        'custom-green-medium': '#8FAF8F',
        'custom-green-dark': '#5C7F5C',
        'custom-green-darkest': '#2F4F2F',
        'custom-light-gray': '#E6E8E5',
      },
      fontFamily: {
        kanit: ['Kanit', 'sans-serif'], // ✅ อยู่ใน fontFamily
      },
    },
  },
  plugins: [],
}