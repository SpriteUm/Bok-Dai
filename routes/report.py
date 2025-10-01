from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields import FloatField, DateField
from models.issue import Issue
from models import db

class ReportForm(FlaskForm):
    category = SelectField('หัวข้อ', choices=[
        ('', '-- เลือกหมวดหมู่ --'),
        ('โครงสร้าง/สิ่งอำนวยความสะดวก', 'โครงสร้าง/สิ่งอำนวยความสะดวก'),
        ('ความสะอาด', 'ความสะอาด'),
        ('ความปลอดภัย', 'ความปลอดภัย'),
        ('ไฟฟ้า', 'ไฟฟ้า'),
        ('อื่นๆ', 'อื่นๆ')
    ], validators=[DataRequired()])
    detail = TextAreaField('รายละเอียด', validators=[DataRequired()])
    date_reported = DateField('วันที่เกิดเหตุ', format='%Y-%m-%d', validators=[DataRequired()])
    location_text = StringField('สถานที่', validators=[DataRequired()])
    urgency = SelectField('ความเร่งด่วน', choices=[
        ('🔴', 'สูงสุด'), ('🟠', 'ปานกลาง'), ('🟢', 'ต่ำ')
    ], validators=[DataRequired()])
    lat = FloatField('Latitude')
    lng = FloatField('Longitude')
    submit = SubmitField('ส่งรายงาน')

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        try:
            issue = Issue(
                category=form.category.data,
                detail=form.detail.data,
                date_reported=form.date_reported.data,
                location_text=form.location_text.data,
                urgency=form.urgency.data,
                lat=form.lat.data if form.lat.data else None,
                lng=form.lng.data if form.lng.data else None,
                user_id=current_user.id
            )
            db.session.add(issue)
            db.session.commit()
            flash("ส่งรายงานเรียบร้อยแล้ว", "success")
            return redirect(url_for('indexuser'))
        except Exception as e:
            db.session.rollback()
            flash("เกิดข้อผิดพลาดในการส่งรายงาน: " + str(e), "error")
    return render_template('report.html', form=form)
