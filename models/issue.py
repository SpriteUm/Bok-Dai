from models import db
from datetime import datetime

class Issue(db.Model):
    __tablename__ = 'issues'

    # ++ เพิ่ม list นี้เข้าไป ++
    # ใช้สำหรับตรวจสอบสถานะที่อนุญาตในไฟล์ routes/admin.py
    ALLOWED_STATUSES = ['รอดำเนินการ', 'กำลังดำเนินการ', 'แก้ไขแล้ว']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    date_reported = db.Column(db.Date, nullable=False)
    location_text = db.Column(db.String(200))
    # NOTE: การใช้ Enum ดีมากครับ ทำให้ข้อมูลใน DB มีความสอดคล้องกัน
    urgency = db.Column(db.Enum('🔴','🟠','🟢', name='urgency_levels'), nullable=False)
    status = db.Column(
        db.Enum(*ALLOWED_STATUSES, name='issue_status'), # อ้างอิงจาก list ด้านบน
        default=ALLOWED_STATUSES[0], # 'รอดำเนินการ'
        nullable=False
    )
    location_link = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    # ความสัมพันธ์กับตารางรูปภาพและประวัติสถานะ
    images = db.relationship('IssueImage', backref='issue', lazy=True, cascade="all, delete-orphan")
    status_history = db.relationship('IssueStatusHistory', backref='issue', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Issue {self.id}>'