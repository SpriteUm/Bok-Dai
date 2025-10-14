from . import db
from datetime import datetime
from .issue import Issue # <-- Import Issue model เพื่อใช้สถานะร่วมกัน

class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key เชื่อมโยงกับรายงานปัญหา (Issue)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    
    # Foreign Key เชื่อมโยงกับผู้ใช้งานที่ทำการอัปเดต (Admin)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # สถานะใหม่ที่ถูกเปลี่ยนไป
    status = db.Column(
        db.Enum(*Issue.ALLOWED_STATUSES, name='issue_status'), # <-- ใช้สถานะจาก Issue model โดยตรง
        nullable=False
    )

    # ++ FIX: แก้ไข 'note' ให้เป็นการประกาศคอลัมน์ที่ถูกต้อง ++
    # หมายเหตุเพิ่มเติม
    notes = db.Column(db.Text, nullable=True) # nullable=True หมายถึงสามารถเว้นว่างได้
    
    # เวลาที่ทำการอัปเดตสถานะ
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ++ IMPROVEMENT: เพิ่ม Relationship ไปยัง User Model ++
    # ทำให้เราสามารถดึงข้อมูลผู้ใช้ที่ทำการแก้ไขได้ง่ายๆ เช่น entry.changer.username
    changer = db.relationship('User')

    def __repr__(self):
        return f"<StatusHistory Issue:{self.issue_id} Status:{self.status} By:{self.changed_by_id}>"