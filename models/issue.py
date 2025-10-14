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
    status = db.Column(db.Enum('รอดำเนินการ','กำลังดำเนินการ','แก้ไขแล้ว', name='issue_status'), default='รอดำเนินการ')
    location_link = db.Column(db.String(300))              # ลิงก์ Google Maps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    status = db.Column(
        db.Enum('รอดำเนินการ', 'กำลังดำเนินการ', 'แก้ไขแล้ว', name='issue_status'),
        default='รอดำเนินการ',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship('IssueImage', backref='issue', lazy=True)
    status_history = db.relationship('IssueStatusHistory', backref='issue', lazy=True)
