from flask import Flask, render_template
from flask_login import LoginManager
from models import db
import os


def create_app():
    app = Flask(name)
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bokdai.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # import blueprints AFTER db.init_app to reduce circular imports
    from routes.auth import auth_bp
    from routes.report import report_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(report_bp, url_prefix="/report")

    @app.route("/")
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


app = create_app()

if name == "main":
    app.run(debug=True)