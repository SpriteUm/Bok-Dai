from models import db
from datetime import datetime

class IssueImage(db.Model):
    __tablename__ = 'issue_images'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # เพิ่มความสัมพันธ์ (optional)
    issue = db.relationship('Issue', backref='images')
