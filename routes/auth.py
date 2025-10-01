from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from models.user import User
from models.issue import IssueReport
from models import db

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

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

class ReportForm(FlaskForm):
    category = SelectField('หัวข้อ', choices=[
        ('', '-- เลือกหมวดหมู่ --'),
        ('โครงสร้าง/สิ่งอำนวยความสะดวก', 'โครงสร้าง/สิ่งอำนวยความสะดวก'),
        ('ความสะอาด', 'ความสะอาด'),
        ('ความปลอดภัย', 'ความปลอดภัย'),
        ('ไฟฟ้า', 'ไฟฟ้า'),
        ('อื่นๆ', 'อื่นๆ')
    ], validators=[DataRequired()])
    location_note = StringField('หมายเหตุ', validators=[DataRequired()])
    map_location = StringField('Google Maps')
    details = TextAreaField('รายละเอียด', validators=[DataRequired()])
    submit = SubmitField('ส่งรายงาน')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("เข้าสู่ระบบเรียบร้อยแล้ว", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('indexuser'))
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
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("เกิดข้อผิดพลาด: " + str(e), "error")
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for('auth.login'))


@auth_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        try:
            report = IssueReport(
                category=form.category.data,
                location_note=form.location_note.data,
                map_location=form.map_location.data,
                details=form.details.data,
                user_id=current_user.id
            )
            db.session.add(report)
            db.session.commit()
            flash("ส่งรายงานเรียบร้อยแล้ว", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash("เกิดข้อผิดพลาดในการส่งรายงาน: " + str(e), "error")
    return render_template('report.html', form=form)
