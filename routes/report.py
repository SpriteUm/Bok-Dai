import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import datetime
from models import db
from models.issue import Issue
from models.issue_image import IssueImage  # ✅ เพิ่มส่วนนี้เข้ามา

# สร้าง Blueprint
report_bp = Blueprint('report', __name__, template_folder='../templates')


# ฟังก์ชันตรวจสอบ/สร้างโฟลเดอร์อัปโหลด
def ensure_upload_folder():
    folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    os.makedirs(folder, exist_ok=True)
    return folder


# ฟอร์มสำหรับรายงานปัญหา
class ReportForm(FlaskForm):
    category = SelectField('หัวข้อ', choices=[
        ('', '-- เลือกหมวดหมู่ --'),
        ('โครงสร้าง/สิ่งอำนวยความสะดวก', 'โครงสร้าง/สิ่งอำนวยความสะดวก'),
        ('ความสะอาด', 'ความสะอาด'),
        ('ความปลอดภัย', 'ความปลอดภัย'),
        ('ไฟฟ้า', 'ไฟฟ้า'),
        ('อื่นๆ', 'อื่นๆ')
    ], validators=[DataRequired()])
    other_text = StringField('อื่นๆ')
    detail = TextAreaField('รายละเอียด', validators=[DataRequired()])
    date_reported = DateField('วันที่เกิดเหตุ', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.utcnow)
    location_text = StringField('สถานที่', validators=[DataRequired()])
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', 'สูงสุด'), ('🟠', 'ปานกลาง'), ('🟢', 'ต่ำ')
    ], validators=[DataRequired()])
    submit = SubmitField('ส่งรายงาน')


# เส้นทางของหน้า report
@report_bp.route('/', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        try:
            # ✅ สร้าง record ของ Issue
            issue = Issue(
                user_id=current_user.id,
                category=form.category.data,
                detail=form.detail.data,
                date_reported=form.date_reported.data or datetime.utcnow().date(),
                location_text=form.location_text.data,
                urgency=form.urgency.data,
                status='รอดำเนินการ',
                lat=None,
                lng=None
            )
            db.session.add(issue)
            db.session.flush()  # ✅ flush เพื่อให้ issue.id ใช้งานได้ก่อน commit

            # ✅ จัดการอัปโหลดรูปภาพ (ถ้ามี)
            upload_folder = ensure_upload_folder()
            files = request.files.getlist('images[]')  # ต้องมี input ชื่อ images[] ใน HTML
            for file in files:
                if file and file.filename != '':
                    filename = file.filename
                    save_path = os.path.join(upload_folder, filename)
                    file.save(save_path)

                    # ✅ บันทึก path ลงในตาราง IssueImage
                    issue_image = IssueImage(
                        issue_id=issue.id,
                        file_path=save_path
                    )
                    db.session.add(issue_image)

            # ✅ commit ทุกอย่างลง DB
            db.session.commit()

            flash("ส่งรายงานและบันทึกรูปภาพเรียบร้อยแล้ว", "success")
            return redirect(url_for('indexuser'))

        except Exception:
            current_app.logger.exception("Error saving Issue or images")
            db.session.rollback()
            flash("เกิดข้อผิดพลาดในการบันทึกรายงาน ดู log ใน terminal", "error")

    return render_template('report.html', form=form)
