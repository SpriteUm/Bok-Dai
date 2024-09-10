# Bok-Dai - Report a problem
## 📌 Project Overview  

ระบบรายงานปัญหาสาธารณะ (Issue Reporting System) พัฒนาขึ้นเพื่อให้นักศึกษา บุคลากร และบุคคลทั่วไป สามารถแจ้งปัญหาต่าง ๆ ได้สะดวก เช่น ไฟฟ้า น้ำ ถนน ขยะ พร้อมแนบรายละเอียด วันเวลา สถานที่ พิกัดแผนที่ ระดับความเร่งด่วน และรูปภาพประกอบ เพื่อให้การสื่อสารกับผู้ดูแลระบบมีความชัดเจนมากขึ้น  
ฝ่ายผู้ดูแลระบบ (Admin) สามารถเข้าสู่ระบบหลังบ้าน (Dashboard) เพื่อดูรายการปัญหาที่ถูกรายงาน อัปเดตสถานะ (กำลังดำเนินการ / แก้ไขแล้ว) และใช้ตัวกรองขั้นสูง เช่น หมวดหมู่ปัญหา ความเร่งด่วน สถานที่ และวันที่แจ้ง รวมถึงสามารถดูตำแหน่งปัญหาบนแผนที่หรือแสดงเป็น **Map View** ได้  

Project นี้ช่วยให้องค์กรสามารถ **จัดการปัญหาสาธารณะได้อย่างมีประสิทธิภาพ** โดยให้ความสำคัญกับความเร่งด่วน โปร่งใสในการติดตาม และสะดวกต่อทั้งผู้ใช้งานและผู้ดูแลระบบ  

## Setup Guide
**Prerequisites**
- Node.js 18.0.0+
- Python 3.10+
- Git
- jinja

**Clone repository and Setup Python Environment**
<pre>
# Clone repository
git clone (repository-url)
cd Bok-Dai

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
</pre>
**Install Node.js Packages & Build Tailwind**
<pre>
# Install dependencies
npm install

# Build TailwindCSS
npm run dev
</pre>
**Setup Environment Variables**
สร้างไฟล์ .env แล้วเพิ่มค่า config

**Run Flask App**
<pre>flask run</pre>

## Project Structure
<pre>
BOKDAI/
├── pycache/              # cache ของ Python
├── node_modules/         # npm dependencies
├── public/               # Static assets (frontend เช่น รูปภาพ favicon ฯลฯ)
├── static/
│   ├── dist/
│   │   └── output.css    # ไฟล์ CSS ที่ build จาก Tailwind
│   └── src/
│       └── input.css     # ไฟล์ CSS ต้นฉบับสำหรับ Tailwind
├── templates/
│   └── index.html        # main template สำหรับ Flask (Jinja2)
├── venv/                 # Python virtual environment
├── .env                  # Environment variables (เช่น DB, SECRET_KEY)
├── .gitignore            # Git ignore rules
├── app.py                # main Flask app (entry point ของ backend)
├── package-lock.json     # lockfile npm
├── package.json          # npm scripts + deps
├── postcss.config.js     # Tailwind/PostCSS config
├── README.md             # documentation
├── requirements.txt      # Python packages
└── tailwind.config.js    # Tailwind config
</pre>

## 📂 รายละเอียดไฟล์สำคัญ

- **app.py**  
  ไฟล์หลักของ Flask backend รวม logic สำหรับรับ request, routing, การเชื่อมต่อฐานข้อมูล, และการ render template

- **requirements.txt**  
  รายการ Python packages ที่จำเป็น เช่น Flask, Jinja2, ฯลฯ

- **package.json**  
  กำหนด dependencies ฝั่ง frontend (เช่น tailwindcss, postcss) และ npm scripts สำหรับ build

- **tailwind.config.js / postcss.config.js**  
  กำหนด config สำหรับ Tailwind CSS และ PostCSS

- **static/src/input.css**  
  ไฟล์ CSS ต้นฉบับที่ใช้เขียน style ด้วย Tailwind

- **static/dist/output.css**  
  ไฟล์ CSS ที่ถูก build แล้วจาก Tailwind สำหรับใช้งานจริง

- **templates/index.html**  
  Template หลักสำหรับแสดงหน้าเว็บ (ใช้ Jinja2)

- **.env**  
  เก็บค่าคอนฟิกสำคัญ เช่น DATABASE_URL, SECRET_KEY, ฯลฯ (ไม่ควร commit ลง git)

- **public/**  
  เก็บไฟล์ static อื่น ๆ เช่น รูปภาพ โลโก้ favicon ฯลฯ

- **venv/**  
  โฟลเดอร์ virtual environment สำหรับ Python

## 🛠️ การทำงานหลัก

- ผู้ใช้สามารถแจ้งปัญหาโดยกรอกฟอร์มและแนบรูปภาพ
- ข้อมูลจะถูกบันทึกลงฐานข้อมูล (เช่น SQLite, PostgreSQL)
- ผู้ดูแลระบบสามารถดูรายการปัญหาและอัปเดตสถานะผ่าน Dashboard
- มีระบบกรองและแสดงตำแหน่งปัญหาบนแผนที่

<<<<<<< HEAD

=======
## 📞 ติดต่อ/แจ้งปัญหาเพิ่มเติม

หากพบปัญหาในการติดตั้งหรือใช้งาน สามารถติดต่อทีมพัฒนาได้ที่ [email/ช่องทางติดต่อ]
>>>>>>> restore-temp

