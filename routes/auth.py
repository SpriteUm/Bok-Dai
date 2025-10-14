from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้ หรือ อีเมล', validators=[DataRequired()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])
    remember = BooleanField('จดจำฉันไว้ในระบบ') # ++ เพิ่ม
    submit = SubmitField('เข้าสู่ระบบ')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired(), EqualTo('password', message='รหัสผ่านจะต้องตรงกัน')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Telephone', validators=[DataRequired()])
    submit = SubmitField('Register')

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('induser.indexuser'))  
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")
            
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # ตรวจสอบ Username ซ้ำ
        if User.query.filter_by(username=form.username.data).first():
            flash('ชื่อผู้ใช้นี้ถูกใช้งานแล้ว', 'error')
            return render_template('register.html', form=form)
        # ตรวจสอบ Email ซ้ำ
        if User.query.filter_by(email=form.email.data).first():
            flash('อีเมลนี้ถูกใช้งานแล้ว', 'error')
            return render_template('register.html', form=form)
        
        try:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                telephone=form.telephone.data
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"เกิดข้อผิดพลาดในการลงทะเบียน: {e}", "error")
            
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
