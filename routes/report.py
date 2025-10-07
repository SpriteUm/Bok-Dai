import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField, HiddenField
from wtforms.validators import DataRequired
from datetime import datetime
from models import db
from models.issue import Issue

report_bp = Blueprint('report', __name__, template_folder='../templates')

def ensure_upload_folder():
    folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    os.makedirs(folder, exist_ok=True)
    return folder

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
    lat = HiddenField('lat')
    lng = HiddenField('lng')
    submit = SubmitField('ส่งรายงาน')


@report_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        try:
            # ✅ เพิ่มส่วนนี้ เพื่อดึงค่าพิกัดจากฟอร์ม (มาจาก Leaflet.js)
            lat_value = form.lat.data or request.form.get("lat")
            lng_value = form.lng.data or request.form.get("lng")

            # (optional) handle uploads if needed
            # upload_folder = ensure_upload_folder()
            # files = request.files.getlist('images[]') ...

            issue = Issue(
                user_id=current_user.id,
                category=form.category.data,
                detail=form.detail.data,
                date_reported=form.date_reported.data or datetime.utcnow().date(),
                location_text=form.location_text.data,
                urgency=form.urgency.data,
                status='รอดำเนินการ',   # หรือรับจากฟอร์มถ้ามี
                # ✅ เพิ่มบรรทัดนี้ เพื่อบันทึกค่าพิกัดจริง
                lat=float(lat_value) if lat_value else None,
                lng=float(lng_value) if lng_value else None
            )

            db.session.add(issue)
            db.session.commit()
            flash("ส่งรายงานเรียบร้อยแล้ว", "success")
            return redirect(url_for('indexuser'))
        except Exception:
            current_app.logger.exception("Error saving Issue")
            db.session.rollback()
            flash("เกิดข้อผิดพลาดในการบันทึกรายงาน ดู log ใน terminal", "error")
    return render_template('report.html', form=form)
