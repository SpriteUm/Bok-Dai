from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required
from models import db
from models.user import User
from models.issue import Issue
from models.issue_image import IssueImage
from models.issue_status_history import IssueStatusHistory
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # สร้าง instance folder ถ้ายังไม่มี
    os.makedirs(app.instance_path, exist_ok=True)

    # เก็บ database ใน instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'bokdai.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["WTF_CSRF_ENABLED"] = True

    # โฟลเดอร์เก็บไฟล์อัปโหลด
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # init db
    db.init_app(app)

    # LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # import blueprints
    from routes.auth import auth_bp
    from routes.report import report_bp
    from routes.indexuser import indexuser_bp
    
    app.register_blueprint(indexuser_bp, url_prefix="/indexuser")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(report_bp, url_prefix="/report")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/indexuser")
    def indexuser():
        return render_template("indexuser.html")

    # import โมเดลทั้งหมดเพื่อ register mapper
    with app.app_context():
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

        db.create_all()  # สร้าง table ทั้งหมด: users, issue, issue_status_history, issue_image

    # user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
