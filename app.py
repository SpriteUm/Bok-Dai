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
        if current_user.is_authenticated:
            if current_user.is_admin:
                # Redirect Admin to Dashboard (which is indexadmin.html)
                return redirect(url_for('admin.dashboard'))
            else:
                # Redirect regular user to their home page (induser.indexuser)
                return redirect(url_for('induser.indexuser'))
        
        # If not logged in, redirect to login page
        return redirect(url_for('auth.login'))

    # Create DB tables if they don't exist
    with app.app_context():
        # NOTE: db.create_all() อาจเป็นสาเหตุของปัญหาถ้า Models/Issue มีปัญหา
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    # เพิ่ม try-except เพื่อให้ server run ได้ และแสดง error ถ้ามีปัญหาอื่นที่ไม่ใช่ Import Error
    try:
        print(f"\n * Starting Flask server...")
        app.run(debug=True, use_reloader=False) # use_reloader=False เพื่อป้องกันการรันซ้ำ
    except Exception as e:
        print(f"\n--- FATAL ERROR DURING SERVER STARTUP ---")
        print(f"Error: {e}")
        print(f"สาเหตุที่พบบ่อย: 1. โมเดล/ตารางมีปัญหา 2. ขาดไฟล์ใน routes/")
