import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate

from models import db, initialize_models

# Optional SocketIO support
try:
    from flask_socketio import SocketIO, join_room, leave_room
    socketio = SocketIO()
    _HAS_SOCKETIO = True
except Exception:
    socketio = None
    _HAS_SOCKETIO = False

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
    Migrate(app, db)

    if _HAS_SOCKETIO and socketio is not None:
        socketio.init_app(app, cors_allowed_origins="*")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "กรุณาเข้าสู่ระบบก่อนเพื่อเข้าถึงหน้านี้"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models.user import User
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    with app.app_context():
        try:
            initialize_models()
        except Exception:
            app.logger.debug("initialize_models() failed or models not present yet")

        # Register blueprints with guarded imports
        try:
            from routes.report import report_bp
            app.register_blueprint(report_bp, url_prefix='/report')
        except Exception:
            app.logger.debug("routes.report not available")

        try:
            from routes.auth import auth_bp
            app.register_blueprint(auth_bp, url_prefix='/auth')
        except Exception:
            app.logger.debug("routes.auth not available")

        try:
            from routes.indexuser import indexuser_bp
            app.register_blueprint(indexuser_bp, url_prefix='/indexuser')
        except Exception:
            app.logger.debug("routes.indexuser not available")

        try:
            from routes.admin import admin_bp
            app.register_blueprint(admin_bp, url_prefix='/admin')
        except Exception:
            app.logger.debug("routes.admin not available")

    if _HAS_SOCKETIO and socketio is not None:
        @socketio.on('join')
        def _on_join(room):
            try:
                join_room(room)
            except Exception:
                pass

        @socketio.on('leave')
        def _on_leave(room):
            try:
                leave_room(room)
            except Exception:
                pass

    @app.route('/')
    def index():
        try:
            from models.issue import Issue
            total_issues = Issue.query.count()
            in_progress_issues = Issue.query.filter_by(status='กำลังดำเนินการ').count()
            resolved_issues = Issue.query.filter_by(status='แก้ไขแล้ว').count()
        except Exception:
            total_issues = in_progress_issues = resolved_issues = 0
            app.logger.exception("Failed to query Issue counts on index")

        return render_template('index.html',
                               total_issues=total_issues,
                               in_progress_issues=in_progress_issues,
                               resolved_issues=resolved_issues)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            app.logger.exception("db.create_all() failed")

    if _HAS_SOCKETIO and socketio is not None:
        socketio.run(app, debug=True)
    else:
        app.run(debug=True)
