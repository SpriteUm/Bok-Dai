from models import db
from datetime import datetime

class IssueImage(db.Model):
    __tablename__ = 'issue_images'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    
    # --- FIX: เปลี่ยนชื่อคอลัมน์จาก file_path เป็น filename ---
    filename = db.Column(db.String(255), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IssueImage {self.filename}>"