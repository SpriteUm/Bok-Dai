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