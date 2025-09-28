from flask import Flask, render_template, redirect, url_for, request
from models import db
from models.user import User
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

# init db
db.init_app(app)

# init login
login_manager = LoginManager()
login_manager.init_app(app)

# ระบุว่า login view คือ route ไหน (ถ้าใช้ login_required)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 👉 หน้าแรกให้เปิด dashboard
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)