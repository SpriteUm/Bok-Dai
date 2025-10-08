import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template
from flask_login import LoginManager
from models import db
from models.user import User
from models.issue import Issue  # ✅ ต้อง import เพื่อให้ db.create_all() สร้างตาราง
from routes.report import report_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------ LOGIN MANAGER ------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ ROUTES ------------------
@app.route('/')
def user():
    return render_template('user.html')  # ✅ หน้าแรกเปิด dashboard

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

# ------------------ BLUEPRINT ------------------
app.register_blueprint(report_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ สร้าง database.db และตาราง issues, users
    app.run(debug=True)