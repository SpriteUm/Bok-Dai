from flask import Flask, render_template
from flask_login import LoginManager
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bokdai.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    # register a user_loader so flask-login can load the current_user
    # import here to avoid circular imports at module import time
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            # user_id may be a string, convert to int for query
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Flask-Login: provide a user_loader so `current_user` can be loaded
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # import blueprints AFTER db.init_app to reduce circular imports
    from routes.auth import auth_bp
    from routes.report import report_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(report_bp, url_prefix="/report")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/indexuser")
    def indexuser():
        return render_template("indexuser.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)