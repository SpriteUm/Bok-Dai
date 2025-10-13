from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# นำเข้า model ทั้งหมดเพื่อให้ Flask รู้จักก่อนสร้างตาราง
from models.user import User
from models.issue import Issue
from models.issue_image import IssueImage
from models.issue_status_history import IssueStatusHistory
