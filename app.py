from flask import Flask, render_template
from flask_login import LoginManager
from models import db
from models.user import User

from routes.auth import auth_bp
from routes.report import report_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "spriteum"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# เชื่อม SQLAlchemy กับแอป
db.init_app(app)

# ลงทะเบียน Blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(report_bp, url_prefix="/report")

# ตั้งค่า Login Manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

# โหลดผู้ใช้จาก session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# หน้าแรกของเว็บ
@app.route("/")
def index():
    return render_template("index.html")

# หน้า user หลัง login สำเร็จ
@app.route("/indexuser")
def indexuser():
    return render_template("indexuser.html")

# สร้างฐานข้อมูลเมื่อรันครั้งแรก
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
