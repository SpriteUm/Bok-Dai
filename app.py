from flask import Flask, render_template
from flask_login import LoginManager
from models import db
import os

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bokdai.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True

    # ตั้งค่าโฟลเดอร์สำหรับอัปโหลดไฟล์
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # เริ่มต้น SQLAlchemy
    db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"   # ย้ำ: endpoint ของ login อยู่ใน blueprint auth
login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

@app.route('/')
def indexuser():
    return render_template('index.html')

# Register blueprint
app.register_blueprint(report_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')


if __name__ == "__main__":
    with app.app_context():
        # Import models เพื่อให้ SQLAlchemy ลงทะเบียน mapper
        import models.user
        import models.issue
        import models.issue_image
        try:
            import models.issue_status_history
        except ImportError:
            try:
                import models.issueStatusHistory
            except ImportError:
                app.logger.warning("IssueStatusHistory model not found; skipping import")

        # สร้างตารางทั้งหมดในฐานข้อมูล
        db.create_all()

    app.run(debug=True)
