# 📱 Bok-Dai (บอกได้) - Public Issue Reporting Mobile App

[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter)](https://flutter.dev)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Bok-Dai (บอกได้)** คือแอปพลิเคชันบนมือถือสำหรับการรายงานปัญหาสาธารณะ (Public Issue Reporting System) พัฒนาขึ้นเพื่อให้นักศึกษา บุคลากร และบุคคลทั่วไป สามารถแจ้งปัญหาต่าง ๆ ภายในพื้นที่หรือองค์กรได้สะดวกและรวดเร็วผ่านสมาร์ตโฟน เช่น ไฟฟ้าขัดข้อง, น้ำประปาไม่ไหล, ถนนชำรุด หรือปัญหาขยะ

---

## 📌 Features (ฟีเจอร์หลัก)

### 👤 สำหรับผู้ใช้งานทั่วไป (User)
* 📸 **ถ่ายภาพและอัปโหลด:** ถ่ายภาพปัญหาจากกล้องมือถือหรือเลือกรูปจาก Gallery
* 📍 **ปักหมุด GPS:** ระบบดึงพิกัดตำแหน่งปัจจุบันให้อัตโนมัติ หรือเลือกปักหมุดบนแผนที่ได้
* 🏷️ **จัดหมวดหมู่ & ความเร่งด่วน:** เลือกประเภทปัญหา (เช่น ไฟฟ้า, น้ำท่วม, ขยะ) และเลือกระดับความเร่งด่วน
* 🔔 **ติดตามสถานะ Realtime:** ดูสถานะการแก้ไขปัญหา (รอดำเนินการ / กำลังดำเนินการ / แก้ไขแล้ว) แบบเรียลไทม์

### 🛡️ สำหรับผู้ดูแลระบบ (Admin)
* 📊 **Admin Dashboard:** ดูรายการปัญหาทั้งหมด แยกตามหมวดหมู่ ความเร่งด่วน และสถานะ
* 🗺️ **Map View:** แสดงตำแหน่งปัญหาทั้งหมดบนแผนที่แบบสัญลักษณ์/หมุด
* 🔄 **อัปเดตสถานะ:** เปลี่ยนสถานะการดำเนินงานพร้อมใส่หมายเหตุหรือรูปภาพผลการแก้ไข

---

## 🛠️ Tech Stack

* **Mobile App:** Flutter (Dart) *(รองรับ iOS & Android)*
* **Backend & Database:** [Supabase](https://supabase.com/)
  * **Database:** PostgreSQL (พร้อม Extension `PostGIS` สำหรับเก็บข้อมูลเชิงพื้นที่/พิกัด GPS)
  * **Authentication:** Supabase Auth (Email / Password)
  * **Storage:** Supabase Storage (สำหรับเก็บรูปภาพปัญหา)
  * **Realtime:** Supabase Realtime Engine (อัปเดตสถานะปัญหาทันที)
* **Maps Service:** Google Maps SDK / Flutter Map (OpenStreetMap)

---

## 📂 Project Structure (โครงสร้างโปรเจกต์)

```text
BOKDAI_MOBILE/
├── assets/                  # ไฟล์ Static เช่น โลโก้, ไอคอน, รูปภาพประกอบ
│   ├── icons/
│   └── images/
├── lib/                     # โค้ดหลักของแอปพลิเคชัน
│   ├── main.dart            # Entry point ของแอปพลิเคชัน
│   ├── config/              # คอนฟิกต่าง ๆ เช่น Supabase Client, App Theme
│   │   └── supabase_config.dart
│   ├── models/              # Data Models (Issue, Category, User Profile)
│   │   ├── issue_model.dart
│   │   └── category_model.dart
│   ├── services/            # Logic การดึง/ส่งข้อมูลกับ Supabase API
│   │   ├── auth_service.dart
│   │   ├── issue_service.dart
│   │   └── storage_service.dart
│   ├── views/               # หน้าจอต่าง ๆ (Screens/Pages)
│   │   ├── auth/            # หน้า Login / Register
│   │   ├── home/            # หน้าหลัก / แสดงรายการปัญหา
│   │   ├── report/          # หน้าฟอร์มแจ้งปัญหา + ปักหมุด GPS + ถ่ายภาพ
│   │   ├── map/             # หน้า Map View แสดงตำแหน่งปัญหาบนแผนที่
│   │   └── admin/           # หน้า Dashboard สำหรับ Admin
│   └── widgets/             # Reusable UI Components
├── .env.example             # ตัวอย่างการตั้งค่า Environment Variables
├── .gitignore               # Git ignore rules
├── pubspec.yaml             # Flutter dependencies & packages
└── README.md                # เอกสารกำกับโปรเจกต์
