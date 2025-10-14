from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# import models ที่เหลือ
from .user import User
from .issue import Issue
from .issueimage import IssueImage
from .issueStatusHistory import IssueStatusHistory
