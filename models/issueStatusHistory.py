from models import db
from datetime import datetime

class IssueStatusHistory(db.Model):
    __tablename__ = 'IssueStatusHistory'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<IssueStatusHistory issue_id={self.issue_id} from={self.old_status} to={self.new_status}>"
