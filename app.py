from flask import Flask, render_template
from models import db
from models.user import User 
from flask_login import LoginManager
from routes.auth import auth_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "x234y5z"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

# register blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")

# init db
db.init_app(app)

# init login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    # หรือใช้ db.session.get(User, int(user_id)) ถ้า SQLAlchemy 2.x

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


