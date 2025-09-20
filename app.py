from flask import Flask, render_template, redirect, url_for, request
from models import db
from models.user import User
from flask_login import LoginManager

app = Flask(__name__)

@app.route("/")
def test():
    return render_template("indexadmin.html")

if __name__ == "__main__":
    app.run(debug=True)