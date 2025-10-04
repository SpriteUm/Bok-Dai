from flask import Flask, render_template
from flask_login import LoginManager
from models import db
from models.user import User
from routes.report import report_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"   # ย้ำ: endpoint ของ login อยู่ใน blueprint auth
    login_manager.init_app(app)

    # import models/user here if you have real User model
    try:
        from models.user import User as UserModel
    except Exception:
        UserModel = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def indexuser():
    return render_template('index.html')

# Register blueprint
app.register_blueprint(report_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
