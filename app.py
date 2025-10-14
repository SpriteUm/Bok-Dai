import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db
from models.user import User
# NOTE: ต้องมั่นใจว่าไฟล์เหล่านี้มีอยู่จริง และไม่มีปัญหา Import ภายใน
from routes.report import report_bp
from routes.auth import auth_bp
from routes.indexuser import indexuser_bp
from routes.admin import admin_bp  # <-- IMPORT ADMIN BLUEPRINT

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "กรุณาเข้าสู่ระบบก่อนเพื่อเข้าถึงหน้านี้"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)
    # register a user_loader so flask-login can load the current_user
    # import here to avoid circular imports at module import time
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            # user_id may be a string, convert to int for query
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Flask-Login: provide a user_loader so `current_user` can be loaded
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints 
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(indexuser_bp, url_prefix='/induser')
    app.register_blueprint(admin_bp, url_prefix='/admin') # <--- Admin Blueprint Registration

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Simple routes (Redirect based on login status)
    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route("/indexuser")
    def indexuser():
        return render_template("indexuser.html")

    # ให้ import โมเดลทั้งหมดที่ต้องการ ให้ SQLAlchemy ลงทะเบียน mapper ก่อน create_all()
    with app.app_context():
        import models.user
        import models.issue
        import models.issue_image
        # try both possible filenames for history module (tolerate naming)
        try:
            import models.issue_status_history
        except ImportError:
            try:
                import models.issueStatusHistory
            except ImportError:
                app.logger.warning("IssueStatusHistory model not found; skipping import")

        db.create_all()

    # user_loader ต้องเรียกหลัง import models.user
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == "__main__":
    app.run(debug=True)
