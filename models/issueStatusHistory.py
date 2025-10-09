from models import db
from datetime import datetime

class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key เชื่อมโยงกับรายงานปัญหา (Issue)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    
    # Foreign Key เชื่อมโยงกับผู้ใช้งานที่ทำการอัปเดต (Admin)
    # ใช้ 'users.id' ตามชื่อตารางใน User Model
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # สถานะใหม่ที่ถูกเปลี่ยนไป
    # ควรใช้ Enum เดียวกันกับที่กำหนดใน Issue Model เพื่อความสอดคล้อง
    status = db.Column(
        db.Enum('รอดำเนินการ', 'กำลังดำเนินการ', 'แก้ไขแล้ว', name='issue_status'),
        nullable=False
    )
    
    # เวลาที่ทำการอัปเดตสถานะ
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<StatusHistory Issue:{self.issue_id} Status:{self.status} By:{self.user_id}>"
