import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import datetime
from models import db
from models.issue import Issue

try:
    from models.issue_image import IssueImage
except ImportError:
    IssueImage = None

report_bp = Blueprint('report', __name__, template_folder='../templates')

def ensure_upload_folder():
    folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads'))
    os.makedirs(folder, exist_ok=True)
    return folder

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

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
    location_link = StringField('ลิงก์ Google Maps')
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', 'สูงสุด'), ('🟠', 'ปานกลาง'), ('🟢', 'ต่ำ')
    ], validators=[DataRequired()])
    submit = SubmitField('ส่งรายงาน')

@report_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()

    if form.validate_on_submit():
        try:
            category_value = form.other_text.data if form.category.data == 'อื่นๆ' and form.other_text.data else form.category.data
            issue = Issue(
                user_id=current_user.id,
                category=category_value,
                detail=form.detail.data,
                date_reported=form.date_reported.data or datetime.utcnow().date(),
                location_text=form.location_text.data,
                location_link=form.location_link.data,
                urgency=form.urgency.data,
                status='รอดำเนินการ'
            )
            db.session.add(issue)
            db.session.flush()

            saved_files = []
            if IssueImage is not None:
                upload_folder = ensure_upload_folder()
                files = request.files.getlist('images[]')
                for f in files:
                    if not f or f.filename == '':
                        continue
                    if not allowed_file(f.filename):
                        flash(f"ไฟล์ {f.filename} ไม่รองรับ", "error")
                        continue
                    safe_name = f"{uuid.uuid4().hex}_{f.filename}"
                    dest = os.path.join(upload_folder, safe_name)
                    f.save(dest)
                    rel_path = os.path.relpath(dest, current_app.root_path)
                    img = IssueImage(issue_id=issue.id, file_path=rel_path)
                    db.session.add(img)
                    saved_files.append(safe_name)

            db.session.commit()
            flash("✅ ส่งรายงานเรียบร้อยแล้ว", "success")
            # แก้ไข redirect ไปหน้า index แทน indexuser
            return redirect(url_for('index'))

        except Exception as e:
            current_app.logger.exception("❌ Error saving Issue:")
            db.session.rollback()
            flash(f"เกิดข้อผิดพลาด: {e}", "error")

    elif request.method == 'POST':
        flash("⚠️ โปรดกรอกข้อมูลให้ครบทุกช่องที่จำเป็น", "error")
        current_app.logger.warning(f"Form errors: {form.errors}")

    return render_template('report.html', form=form)
