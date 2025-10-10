from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# import model หลังจากสร้าง db
from .user import User
from .issue import Issue
from .issueimage import IssueImage
from .issueStatusHistory import IssueStatusHistory