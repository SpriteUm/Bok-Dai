import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename

from models import db
from models.issue import Issue
from models.issueimage import IssueImage

report_bp = Blueprint('report', __name__, template_folder='../templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGES = 5

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    date_reported = DateField('วันที่เกิดเหตุ', format='%Y-%m-%d', default=lambda: datetime.utcnow().date(), validators=[DataRequired()])

    # <-- เพิ่มฟิลด์นี้เพื่อให้เทมเพลตเรียกใช้งานได้โดยไม่เกิดข้อผิดพลาด
    location_text = StringField('สถานที่', validators=[Optional()])

    location_link = StringField('ลิงก์ Google Maps', validators=[Optional()])
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', '🔴 เร่งด่วนมาก'), ('🟠', '🟠 ปานกลาง'), ('🟢', '🟢 ไม่เร่งด่วน')
    ], validators=[DataRequired(message="กรุณาเลือกระดับความเร่งด่วน")])
    images = MultipleFileField('แนบรูปภาพ (สูงสุด 5 รูป)')
    submit = SubmitField('ส่งเรื่อง')

@report_bp.route('/', methods=['GET', 'POST'])  # ให้ตรงกับ app.register_blueprint(report_bp, url_prefix='/report')
@login_required
def report():
    form = ReportForm()

    if form.validate_on_submit():
        try:
            # category
            category_value = form.other_text.data.strip() if form.category.data == 'อื่นๆ' and form.other_text.data else form.category.data

            # build payload only with columns that exist on Issue
            payload = {
                "user_id": current_user.id,
                "category": category_value,
                "detail": form.detail.data,
                # DateField returns date -> Issue.date_reported is db.Date
                "date_reported": form.date_reported.data if form.date_reported.data else datetime.utcnow().date(),
                "location_link": form.location_link.data,
                # urgency is stored as emoji in your model
                "urgency": form.urgency.data,
                "status": 'รอดำเนินการ'
            }

            valid_cols = {c.name for c in Issue.__table__.columns}
            filtered = {k: v for k, v in payload.items() if k in valid_cols}

            new_issue = Issue(**filtered)
            db.session.add(new_issue)
            db.session.flush()  # ensure id available for images

            # save uploaded images (WTForms provides files in form.images.data; fallback to request.files)
            files = form.images.data if getattr(form, 'images', None) and form.images.data else request.files.getlist('images')
            saved_count = 0
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for f in files:
                if not f or saved_count >= MAX_IMAGES:
                    continue
                fname = getattr(f, "filename", "")
                if not fname:
                    continue
                if allowed_file(fname):
                    safe = secure_filename(fname)
                    unique = f"{uuid.uuid4().hex}_{safe}"
                    path = os.path.join(upload_folder, unique)
                    f.save(path)
                    img = IssueImage(issue_id=new_issue.id, filename=unique)
                    db.session.add(img)
                    saved_count += 1
                else:
                    flash(f"ไฟล์ {fname} ไม่รองรับ (อนุญาต: {', '.join(sorted(ALLOWED_EXTENSIONS))})", "error")

            db.session.commit()
            current_app.logger.info("Issue created id=%s by user=%s (images=%s)", new_issue.id, current_user.id, saved_count)
            flash('แจ้งปัญหาเรียบร้อยแล้ว', 'success')
            return redirect(url_for('indexuser.indexuser'))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error creating issue")
            flash('เกิดข้อผิดพลาดในการบันทึกข้อมูล โปรดลองอีกครั้ง', 'error')

    elif request.method == 'POST':
        for field, errors in form.errors.items():
            label = getattr(form, field).label.text if hasattr(form, field) else field
            for e in errors:
                flash(f"ข้อผิดพลาดในช่อง '{label}': {e}", "error")

    return render_template('report.html', form=form)
