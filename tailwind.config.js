module.exports = {
  content: ["./templates/**/*.{html,htm}"],
  theme: {
    extend: {
      colors: {
        // โทนสีเทา (สำหรับตัวอักษรเทาอ่อนตามที่คุณต้องการ)
        'custom-light-gray': {
          DEFAULT: '#E6E8E5', // #E6E8E5 - สำหรับใช้เป็นสีตัวอักษร
        },
        // โทนสีเขียวที่คุณกำหนด
        'custom-green': {
          lightest: '#E6E8E5', // พื้นหลัง: #E6E8E5 (เทาอ่อน/เขียวอ่อนมาก)
          dullgreen : '#C2D3C2', // เขียวหม่น: #C2D3C2 (color)
          medium: '#8FAF8F', // เขียวกลาง: #8FAF8F (border-color)
          dark: '#5C7F5C', // เขียวเข้ม: #5C7F5C (background-color)
          darkest: '#2F4F2F', // เขียวมืด: #2F4F2F (color)
        },
      },
    },
  },
  plugins: [],
}
