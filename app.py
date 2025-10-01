from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from routes.auth import auth_bp
from models import db
from models.user import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "spriteum"  # เปลี่ยนได้ตามต้องการ
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bokdai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# เชื่อม SQLAlchemy กับแอป
db.init_app(app)

# ลงทะเบียน Blueprint สำหรับ auth
app.register_blueprint(auth_bp, url_prefix="/auth")

# ตั้งค่า Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# โหลดผู้ใช้จาก session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# หน้าแรกของเว็บ
@app.route("/")
def index():
    return render_template("index.html")  # หน้าแรกก่อน login

# หน้า user หลัง login สำเร็จ
@app.route("/indexuser")
def indexuser():
    return render_template("indexuser.html")  # หน้า user หลัง login

# สร้างฐานข้อมูลเมื่อรันครั้งแรก
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)