from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# กำหนด database ใน instance folder
db_path = os.path.join(app.instance_path, 'bokdai.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# สร้าง instance folder ถ้ายังไม่มี
os.makedirs(app.instance_path, exist_ok=True)

# สร้าง SQLAlchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import models หลังจาก db ถูก bind กับ app
from models.user import User
from models.issue import Issue
from models.issue_image import IssueImage
from models.issue_status_history import IssueStatusHistory

@app.route('/')
def index():
    issues = Issue.query.all()
    return f"มีทั้งหมด {len(issues)} รายการในระบบ"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # สร้าง table ใน instance/bokdai.db
        print("Database & Tables created in instance folder!")
    app.run(debug=True)
