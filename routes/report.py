import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from datetime import datetime
from models.report_model import db, Report

report_bp = Blueprint('report', __name__, template_folder='../templates')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    date_reported = DateField('วันที่เกิดเหตุ', format='%Y-%m-%d', validators=[DataRequired()])
    location_text = StringField('สถานที่', validators=[DataRequired()])
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', 'สูงสุด'), ('🟠', 'ปานกลาง'), ('🟢', 'ต่ำ')
    ], validators=[DataRequired()])
    lat = StringField('ละติจูด')
    lng = StringField('ลองจิจูด')
    submit = SubmitField('ส่งรายงาน')

@report_bp.route('/', methods=['GET','POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        # เก็บรูป
        filenames = []
        files = request.files.getlist('images[]')
        for f in files:
            if f.filename:
                fname = secure_filename(f.filename)
                f.save(os.path.join(UPLOAD_FOLDER, fname))
                filenames.append(fname)

        # บันทึกลง database
        new_report = Report(
            category=form.category.data,
            other_text=form.other_text.data,
            detail=form.detail.data,
            date_reported=form.date_reported.data,
            location_text=form.location_text.data,
            urgency=form.urgency.data,
            lat=float(form.lat.data) if form.lat.data else None,
            lng=float(form.lng.data) if form.lng.data else None,
            image_filenames=",".join(filenames)
        )
        db.session.add(new_report)
        db.session.commit()

        flash("ส่งรายงานเรียบร้อยแล้ว!", "success")
        return redirect(url_for('report.report'))

    return render_template('report.html', form=form)
