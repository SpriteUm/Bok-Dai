from models import db
from datetime import datetime

class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    google_maps_link = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_filename = db.Column(db.String(255))
    status = db.Column(db.String(50), default='รอดำเนินการ')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ความสัมพันธ์
    images = db.relationship('IssueImage', backref='issue', lazy=True, cascade='all, delete')
    histories = db.relationship('IssueStatusHistory', backref='issue', lazy=True, cascade='all, delete')
