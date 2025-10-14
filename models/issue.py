from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from datetime import datetime

class Issue(db.Model):
    __tablename__ = 'issues'

    # สถานะที่อนุญาตให้ใช้ในระบบ
    ALLOWED_STATUSES = ['รอดำเนินการ', 'กำลังดำเนินการ', 'แก้ไขแล้ว']

    id = db.Column(db.Integer, primary_key=True)

    # ผู้ใช้ที่แจ้งปัญหา
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # หมวดหมู่ของปัญหา เช่น ไฟฟ้า, น้ำ, อินเทอร์เน็ต
    category = db.Column(db.String(100), nullable=False)

    # รายละเอียดของปัญหา
    detail = db.Column(db.Text, nullable=False)

    # วันที่แจ้งปัญหา
    date_reported = db.Column(db.Date, nullable=False)

    # ข้อความระบุสถานที่
    location_text = db.Column(db.String(200))

    # ความเร่งด่วน (ใช้ emoji เพื่อแสดงระดับ)
    urgency = db.Column(
        db.Enum('🔴', '🟠', '🟢', name='urgency_levels'),
        nullable=False
    )

    # สถานะของปัญหา (อิงจาก ALLOWED_STATUSES)
    status = db.Column(
        db.Enum(*ALLOWED_STATUSES, name='issue_status'),
        default=ALLOWED_STATUSES[0],
        nullable=False
    )

    # เวลาที่สร้างและอัปเดต
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    # รูปภาพที่แนบกับปัญหา
    images = db.relationship(
        'IssueImage',
        backref='issue',
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ประวัติการเปลี่ยนสถานะ
    status_history = db.relationship(
        'IssueStatusHistory',
        backref='issue',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<Issue {self.id}>'