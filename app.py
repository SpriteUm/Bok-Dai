from flask import Flask, render_template
from flask_login import LoginManager, UserMixin, login_required
from routes.report import report_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# ตัวอย่าง User class แบบง่าย
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# ตัวอย่าง user loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def indexuser():
    return render_template('index.html')

# Register blueprint
app.register_blueprint(report_bp)

if __name__ == '__main__':
    app.run(debug=True)
