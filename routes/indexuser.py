from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from models.user import User
from models import db
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash

indexuser_bp = Blueprint('induser', __name__)

@indexuser_bp.route('/indexuser')
@login_required
def indexuser():
    return render_template('indexuser.html')