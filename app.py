from flask import Flask, render_template, redirect, url_for, request
from models import db
from models.user import User
from flask_login import LoginManager

app = Flask(__name__)

@app.route("/")
def test():
    return render_template("index.html")

@app.route("/")
def index():
    return render_template("indexuser.html")  # เปลี่ยนชื่อไฟล์ให้ตรง

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # สร้างตารางใน app.db
    app.run(debug=True)