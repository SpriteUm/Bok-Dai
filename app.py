from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db
from models.user import User
from routes.report import report_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "x234y5z"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

# register blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")

# init db
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
<<<<<<<<< Temporary merge branch 1
    return render_template("indexuser.html")  # เปลี่ยนชื่อไฟล์ให้ตรง
=========
    return render_template("")
>>>>>>>>> Temporary merge branch 2

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # สร้างตารางใน app.db
    app.run(debug=True)

