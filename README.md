📌 Project Overview (ภาพรวมโครงการ)
Bok-Dai (บอกได้) เป็นแอปพลิเคชันบนมือถือสำหรับการรายงานปัญหาสาธารณะ (Issue Reporting System) พัฒนาขึ้นเพื่อให้นักศึกษา บุคลากร และบุคคลทั่วไป สามารถแจ้งปัญหาต่าง ๆ ภายในพื้นที่หรือองค์กรได้สะดวกและรวดเร็วผ่านสมาร์ตโฟน เช่น ไฟฟ้าขัดข้อง, น้ำประปาไม่ไหล, ถนนชำรุด หรือปัญหาขยะ

ผู้ใช้งานสามารถถ่ายภาพจากกล้อง แนบพิกัด GPS บนแผนที่ เลือกหมวดหมู่ และกำหนดระดับความเร่งด่วนส่งตรงไปยังผู้ดูแลระบบได้ทันที ระบบทำงานร่วมกับ Supabase ในการจัดการฐานข้อมูล (PostgreSQL), จัดเก็บรูปภาพ (Storage) และแจ้งเตือนสถานะแบบเรียลไทม์ (Realtime)

ฝ่ายผู้ดูแลระบบ (Admin) สามารถดูรายการปัญหา อัปเดตสถานะ (กำลังดำเนินการ / แก้ไขแล้ว) กรองข้อมูลตามหมวดหมู่หรือความเร่งด่วน และดูตำแหน่งปัญหาทั้งหมดบน Map View เพื่อการบริหารจัดการปัญหาสาธารณะได้อย่างมีประสิทธิภาพ โปร่งใส และตรวจสอบได้

🛠️ Tech Stack
Mobile App Framework: Flutter (Dart) หรือ React Native (Expo)
Backend & Database: Supabase
Database: PostgreSQL (พร้อม PostGIS สำหรับเก็บพิกัดแผนที่)
Authentication: Supabase Auth (Email/Password, Social Login)
Storage: Supabase Bucket (จัดเก็บรูปภาพปัญหา)
Realtime: Supabase Realtime (อัปเดตสถานะปัญหาทันที)
Maps Integration: Google Maps SDK / Flutter Map (OpenStreetMap)

🚀 Setup Guide (ขั้นตอนการติดตั้งและตั้งค่า)
Prerequisites
Flutter SDK 3.x+ (หรือ Node.js 18+ หากใช้ React Native)
Git
บัญชี Supabase (สำหรับสร้าง Project และรับค่า API Key)

1. Clone Repository & Install Dependencies
Bash
# Clone repository
git clone (repository-url)
cd Bok-Dai

# Install Mobile App Dependencies (กรณี Flutter)
flutter pub get

# (กรณี React Native / Expo)
# npm install
2. Setup Environment Variables
สร้างไฟล์ .env ไว้ที่ Root ของโปรเจกต์ และใส่ค่าการเชื่อมต่อจาก Supabase Dashboard:

Code snippet
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
3. Setup Supabase Database
เข้าไปที่ Supabase Console -> SQL Editor

รัน SQL Script เพื่อสร้างตาราง issues, categories และตั้งค่า Storage Bucket (ดูโครงสร้าง SQL ในหมวดถัดไป)

4. Run Application
Bash
# รันแอปพลิเคชันบน Emulator / เครื่องจริง (Flutter)
flutter run
📂 Project Structure (โครงสร้างโปรเจกต์)
(ตัวอย่างโครงสร้างโปรเจกต์สไตล์ Flutter/React Native Clean Architecture)

Plaintext
BOKDAI_MOBILE/
├── assets/                  # ไฟล์ Static เช่น โลโก้, ไอคอน, รูปภาพประกอบ
│   ├── icons/
│   └── images/
├── lib/                     # โค้ดหลักของแอปพลิเคชัน (Flutter)
│   ├── main.dart            # Entry point ของแอปพลิเคชัน
│   ├── config/              # คอนฟิกต่างๆ เช่น Supabase Client, Theme
│   │   └── supabase_config.dart
│   ├── models/              # Data Models (Issue, Category, User)
│   │   ├── issue_model.dart
│   │   └── category_model.dart
│   ├── services/            # รวม Logic การดึง/ส่งข้อมูลกับ Supabase
│   │   ├── auth_service.dart
│   │   ├── issue_service.dart
│   │   └── storage_service.dart
│   ├── views/               # หน้าจอต่างๆ (Screens/Pages)
│   │   ├── auth/            # หน้า Login / Register
│   │   ├── home/            # หน้าหลัก / แสดงรายการปัญหา
│   │   ├── report/          # หน้าฟอร์มแจ้งปัญหา + ปักหมุด GPS + ถ่ายภาพ
│   │   ├── map/             # หน้า Map View แสดงตำแหน่งปัญหาบนแผนที่
│   │   └── admin/           # หน้า Dashboard สำหรับ Admin
│   └── widgets/             # Reusable UI Components (Cards, Buttons, Inputs)
├── .env.example             # ตัวอย่างการตั้งค่า Environment Variables
├── .gitignore               # Git ignore rules
├── pubspec.yaml             # Flutter dependencies & packages
└── README.md                # เอกสารกำกับโปรเจกต์
📄 รายละเอียดส่วนสำคัญ
lib/config/supabase_config.dart

ไฟล์เชื่อมต่อและเริ่มต้นการทำงานของ Supabase Client ด้วย URL และ Anon Key
lib/services/issue_service.dart
ฟังก์ชันจัดการ CRUD ข้อมูลปัญหา เช่น การส่งฟอร์มแจ้งปัญหาใหม่ (insert), การดึงรายการปัญหา (select), และการอัปเดตสถานะ (update)
lib/services/storage_service.dart
ฟังก์ชันจัดการการอัปโหลดไฟล์รูปภาพที่ถ่ายจากกล้องขึ้นไปเก็บไว้ที่ Supabase Storage Bucket พร้อมส่ง URL กลับมาบันทึกลงใน Database
lib/views/report/
หน้าฟอร์มที่รวมเซนเซอร์ของมือถือเข้าไว้ด้วยกัน ได้แก่ การเปิดกล้องถ่ายรูป (Camera API) และการดึงพิกัด ละติจูด/ลองจิจูด ปัจจุบัน (GPS/Location API)
Supabase Database & RLS
ใช้ระบบ Row Level Security (RLS) ของ Supabase เพื่อควบคุมสิทธิ์การเข้าถึงข้อมูล เช่น ผู้ใช้ทั่วไปสร้างและดูรายการได้ แต่น้องจาก Admin เท่านั้นที่เปลี่ยนสถานะปัญหาได้

🛠️ การทำงานหลัก (Core Workflows)
การแจ้งปัญหา (User Reporting Workflow):
ผู้ใช้เปิดแอปพลิเคชัน กดปุ่ม "แจ้งปัญหา"
เลือกหมวดหมู่, ใส่ชื่อเรื่อง และรายละเอียด
ถ่ายภาพปัญหาจากกล้องมือถือ หรือเลือกจาก Gallery (ภาพถูกอัปโหลดไปที่ Supabase Storage)
ระบบดึงพิกัด GPS อัตโนมัติ หรือให้ผู้ใช้ปรับปักหมุดบนแผนที่
บันทึกข้อมูลทั้งหมดลง Supabase Database
การติดตามและจัดการปัญหา (Admin & Status Workflow):
Admin เข้าใช้งานส่วน Dashboard บนแอปเพื่อดูรายการปัญหาทั้งหมด
สามารถดูตำแหน่งปัญหาบนแผนที่แบบ Realtime Map View
Admin กดเปลี่ยนสถานะ (เช่น Pending ➔ In Progress ➔ Resolved)
ระบบส่งการอัปเดตสถานะกลับไปยังแอปของผู้แจ้งทันทีผ่าน Supabase Realtime
