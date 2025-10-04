from flask import Flask, render_template
from flask_login import LoginManager
from models import db
from models.user import User
from routes.report import report_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route("/")
def index():
    return render_template("register.html")
