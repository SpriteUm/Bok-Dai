from flask import Flask, render_template
from models import db
from models.user import User
from flask_login import LoginManager
from routes.auth import auth_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "spriteum"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(auth_bp, url_prefix="/auth")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/indexuser")
def indexuser():
    return render_template("indexuser.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
