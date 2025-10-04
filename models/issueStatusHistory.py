from models import db
from flask_login import UserMixin
from datetime import datetime

class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    old_status = db.Column(db.Enum('รอดำเนินการ','กำลังดำเนินการ','แก้ไขแล้ว', name='issue_status'), nullable=False)
    new_status = db.Column(db.Enum('รอดำเนินการ','กำลังดำเนินการ','แก้ไขแล้ว', name='issue_status'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Admin ที่อัปเดต
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)