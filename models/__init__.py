from flask_sqlalchemy import SQLAlchemy

# create the SQLAlchemy db object
db = SQLAlchemy()

# import model classes so that when `from models import db` is used,
# all model classes are already defined and SQLAlchemy can configure
# relationships that reference other mapped classes.
from .user import User
from .issue import Issue
from .issue_image import IssueImage
from .issueStatusHistory import IssueStatusHistory

# import model หลังจากสร้าง db
from .user import User
from .issue import Issue
from .issueimage import IssueImage
from .issueStatusHistory import IssueStatusHistory