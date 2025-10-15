from datetime import datetime
from . import db

# ถ้ามี constants ให้รองรับ (ไม่บังคับ)
try:
    from .constants import ALLOWED_STATUSES
except Exception:
    ALLOWED_STATUSES = None

class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)

    # relationship กับ Issue (back_populates กับ Issue.status_history)
    issue = db.relationship('Issue', back_populates='status_history')

    # DB column ชื่อจริง (จาก schema ที่คุณมี) คือ 'chang_id'
    changed_by_id = db.Column('chang_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    # optional relationship กับ User ถ้ามี models.user.User
    try:
        from .user import User
        changer = db.relationship('User', foreign_keys=[changed_by_id], uselist=False)
    except Exception:
        changer = None

    # status (เก็บเป็น string / enum ขึ้นกับ environment)
    if ALLOWED_STATUSES:
        status = db.Column(db.Enum(*ALLOWED_STATUSES, name='issue_status'), nullable=False)
    else:
        status = db.Column(db.String(64), nullable=False)

    # DB column จริงสำหรับ notes คือ 'note'
    notes = db.Column('note', db.Text, nullable=True)

    # DB column จริงสำหรับไฟล์คือ 'response_id' แต่ในโค้ดใช้ attribute ชื่อ response_image
    response_image = db.Column('response_id', db.String(255), nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<IssueStatusHistory id={self.id} issue_id={self.issue_id} status={self.status} by={self.changed_by_id}>"
