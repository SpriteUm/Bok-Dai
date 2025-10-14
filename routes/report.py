import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional
from datetime import datetime
from werkzeug.utils import secure_filename

from models import db
from models.issue import Issue
from models.issueimage import IssueImage

report_bp = Blueprint('report', __name__, template_folder='../templates')

# --- Helper Function ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Form Definition ---
class ReportForm(FlaskForm):
    category = SelectField('หัวข้อ', choices=[
        ('', '-- เลือกหมวดหมู่ --'),
        ('โครงสร้าง/สิ่งอำนวยความสะดวก', 'โครงสร้าง/สิ่งอำนวยความสะดวก'),
        ('ความสะอาด', 'ความสะอาด'),
        ('ความปลอดภัย', 'ความปลอดภัย'),
        ('ไฟฟ้า', 'ไฟฟ้า'),
        ('อื่นๆ', 'อื่นๆ')
    ], validators=[DataRequired(message="กรุณาเลือกหมวดหมู่")])
    
    other_text = StringField('ระบุหมวดหมู่อื่นๆ', validators=[Optional()])
    
    detail = TextAreaField('รายละเอียด', validators=[DataRequired(message="กรุณากรอกรายละเอียด")])
    date_reported = DateField('วันที่เกิดเหตุ', format='%Y-%m-%d', default=datetime.utcnow, validators=[DataRequired()])
    location_text = StringField('สถานที่', validators=[DataRequired(message="กรุณาระบุสถานที่")])
    location_link = StringField('ลิงก์ Google Maps', validators=[Optional()])
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', '🔴 เร่งด่วนมาก'), ('🟠', '🟠 ปานกลาง'), ('🟢', '🟢 ไม่เร่งด่วน')
    ], validators=[DataRequired(message="กรุณาเลือกระดับความเร่งด่วน")])
    
    images = MultipleFileField('แนบรูปภาพ (สูงสุด 5 รูป)')
    submit = SubmitField('ส่งเรื่อง')

# --- Routes ---
@report_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()

    if form.validate_on_submit():
        try:
            if form.category.data == 'อื่นๆ' and form.other_text.data:
                category_value = form.other_text.data.strip()
            else:
                category_value = form.category.data

            new_issue = Issue(
                user_id=current_user.id,
                category=category_value,
                detail=form.detail.data,
                date_reported=form.date_reported.data,
                location_link=form.location_link.data,
                urgency=form.urgency.data,
                # --- ++ FIX: เพิ่มสถานะเริ่มต้นให้ปัญหาใหม่ ++ ---
                status='รอดำเนินการ'
            )
            db.session.add(new_issue)
            db.session.flush()

            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for file in form.images.data:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file.save(os.path.join(upload_folder, unique_filename))
                    new_image = IssueImage(issue_id=new_issue.id, filename=unique_filename)
                    db.session.add(new_image)

            db.session.commit()
            flash('แจ้งปัญหาเรียบร้อยแล้ว ขอบคุณสำหรับข้อมูลครับ', 'success')
            return redirect(url_for('indexuser.indexuser'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating issue: {e}")
            flash('เกิดข้อผิดพลาดในการบันทึกข้อมูล', 'error')
    
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"ข้อผิดพลาดในช่อง '{getattr(form, field).label.text}': {error}", "error")

    return render_template('report.html', form=form)