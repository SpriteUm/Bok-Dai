from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
        EqualTo('confirm_password', message='รหัสผ่านจะต้องตรงกัน'),
        ])
    # เพิ่ม custom validation สำหรับความยาวรหัสผ่าน
    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired(), EqualTo('password', message='รหัสผ่านจะต้องตรงกัน')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Telephone', validators=[DataRequired()])
    submit = SubmitField('Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('indexuser.indexuser'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('indexuser.indexuser'))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        has_error = False
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append("ชื่อผู้ใช้นี้ถูกใช้แล้ว")
            has_error = True
        if User.query.filter_by(email=form.email.data).first():
            form.email.errors.append("อีเมลนี้ถูกใช้แล้ว")
            has_error = True
        if has_error:
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
            flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("เกิดข้อผิดพลาด: " + str(e), "error")
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required # ต้องล็อกอินก่อนถึงจะออกได้
def logout():
    logout_user()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'success')
    return render_template('index.html')
