import os
from flask import Flask, render_template
from flask_login import LoginManager
from models import db          # ต้องมี models/__init__.py ที่สร้าง SQLAlchemy() เป็น db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ เพิ่มโฟลเดอร์สำหรับเก็บไฟล์แนบจากรายงาน
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"   # ย้ำ: endpoint ของ login อยู่ใน blueprint auth
login_manager.init_app(app)

# import models/user here if you have real User model
try:
    from models.user import User as UserModel
except Exception:
    UserModel = None

@login_manager.user_loader
def load_user(user_id):
    if UserModel:
        return UserModel.query.get(int(user_id))
    return None

# import blueprints AFTER db.init_app to avoid circular imports
from routes.auth import auth_bp
from routes.report import report_bp

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(report_bp, url_prefix="/report")

# simple routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/indexuser")
def indexuser():
    return render_template("indexuser.html")

if __name__ == '__main__':
    with app.app_context():
        # ✅ สร้างโฟลเดอร์อัปโหลดถ้ายังไม่มี
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
    app.run(debug=True)
