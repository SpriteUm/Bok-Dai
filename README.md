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
├── pycache/ # cache ของ Python
├── node_modules/ # npm dependencies
├── public/ # Static assets (frontend)
├── static/
│ ├── dist/
│ │ └── output.css # Tailwind build
│ └── src/
│ └── input.css # Tailwind source
├── templates/
│ └── index.html # main template
├── venv/ # Python virtual environment
├── .env # Environment variables
├── .gitignore # Git ignore rules
├── app.py # main Flask app
├── package-lock.json # lockfile npm
├── package.json # npm scripts + deps
├── postcss.config.js # Tailwind/PostCSS config
├── README.md # documentation
├── requirements.txt # Python packages
└── tailwind.config.js # Tailwind config
</pre>

