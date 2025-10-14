import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate 
from models import db
from models.user import User

from models import db, User, Issue
from routes.report import report_bp
from routes.auth import auth_bp
from routes.indexuser import indexuser_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- Config ---
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Database ---
    db.init_app(app)
    migrate = Migrate(app, db)  # ✅ เพิ่มส่วนนี้ให้รองรับ migration

    # --- Login Manager ---
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "กรุณาเข้าสู่ระบบเพื่อใช้งานส่วนนี้"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # --- Register Blueprints ---
    app.register_blueprint(report_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(indexuser_bp)  # ✅ ไม่มี url_prefix เพื่อให้ /api/issues ใช้งานได้
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --- Route หลัก ---
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/indexuser')
    def indexuser():
        return render_template('indexuser.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboardr.html')

    return app

# --- Run App ---
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
