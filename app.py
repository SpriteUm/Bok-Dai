import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from models import db
from models.user import User
from models.issue import Issue

from routes.report import report_bp
from routes.auth import auth_bp
from routes.indexuser import indexuser_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- Create instance folder ---
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # --- Config ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Database setup ---
    db.init_app(app)
    migrate = Migrate(app, db)

    # --- Login Manager ---
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "กรุณาเข้าสู่ระบบก่อนเพื่อเข้าถึงหน้านี้"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # --- Register Blueprints ---
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(indexuser_bp, url_prefix='/indexuser')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --- Routes ---
    @app.route('/')
    def index():
        total_issues = Issue.query.count()
        in_progress_issues = Issue.query.filter_by(status='กำลังดำเนินการ').count()
        resolved_issues = Issue.query.filter_by(status='แก้ไขแล้ว').count()
        return render_template('index.html',
                               total_issues=total_issues,
                               in_progress_issues=in_progress_issues,
                               resolved_issues=resolved_issues)

    return app

# --- Run App ---
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
