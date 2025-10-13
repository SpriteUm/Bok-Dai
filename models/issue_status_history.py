from models import db
from datetime import datetime

class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<IssueStatusHistory {self.issue_id}: {self.previous_status} -> {self.new_status}>"
