from flask import Flask, render_template
from flask_login import LoginManager
from models import db          # ต้องมี models/__init__.py ที่สร้าง SQLAlchemy() เป็น db

app = Flask(__name__)

@app.route("/")
def test():
    return render_template("admin.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # สร้างตารางใน app.db
    app.run(debug=True)

@app.route("/")
def index():
    return render_template("register.html")
