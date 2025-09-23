from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from models import db

class FormUsers(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                         validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Telephone')
    submit = SubmitField('Register')

auth_bp = Blueprint('auth', __name__) 

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST': 
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password): 
            login_user(user)
            return redirect(url_for('index')) # เปลี่ยน 'index' เป็นชื่อฟังก์ชันที่คุณต้องการให้ไปหลังจากล็อกอิน
        else:
            flash('Invalid username or password') #
    return render_template('login.html') 

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = FormUsers()
    if form.validate_on_submit():
        # ตรวจสอบ username/email ซ้ำ
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists", "error")
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", "error")
            return render_template('register.html', form=form)
        try:
            hashed_password = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                telephone=form.telephone.data
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created!", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('auth.login'))

