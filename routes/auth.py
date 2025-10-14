from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField # ++ เพิ่ม BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length # ++ เพิ่ม Length

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
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('อีเมล', validators=[DataRequired(), Email()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('ยืนยันรหัสผ่าน', validators=[DataRequired(), EqualTo('password', message='รหัสผ่านต้องตรงกัน')])
    first_name = StringField('ชื่อจริง', validators=[DataRequired()])
    last_name = StringField('นามสกุล', validators=[DataRequired()])
    telephone = StringField('เบอร์โทรศัพท์', validators=[DataRequired()])
    submit = SubmitField('ลงทะเบียน')

# --- Routes ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # ถ้าผู้ใช้ล็อกอินอยู่แล้ว ให้ redirect ไปยังหน้าที่ถูกต้องเลย
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('indexuser.indexuser'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # ++ เพิ่มการจดจำผู้ใช้ ++
            login_user(user, remember=form.remember.data)
            
            # --- **** FIX: เพิ่ม Logic การ Redirect **** ---
            # ถ้าเป็น Admin ให้ไปหน้า admin dashboard
            if user.is_admin:
                flash('เข้าสู่ระบบในฐานะผู้ดูแลสำเร็จ!', 'success')
                return redirect(url_for('admin.dashboard'))
            # ถ้าเป็นผู้ใช้ทั่วไป ให้ไปหน้า indexuser
            else:
                flash(f'สวัสดีคุณ {user.username}, เข้าสู่ระบบสำเร็จ!', 'success')
                return redirect(url_for('indexuser.indexuser'))
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
            flash('ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"เกิดข้อผิดพลาดในการลงทะเบียน: {e}", "error")
            
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('คุณได้ออกจากระบบเรียบร้อยแล้ว', 'info') # ++ เพิ่ม
    return redirect(url_for('index')) # <-- ส่งกลับไปหน้า Landing Page