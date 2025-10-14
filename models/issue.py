from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from datetime import date

# สร้าง Blueprint สำหรับ issue
issue_bp = Blueprint('issue', __name__, url_prefix='/issues')

# --- หน้าแสดงรายการปัญหา ---
@issue_bp.route('/')
@login_required
def list_issues():
    issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc()).all()
    return render_template('issues.html', issues=issues)

# --- API สำหรับดึงข้อมูลปัญหา (ใช้ใน indexissue.html) ---
@issue_bp.route('/api')
@login_required
def issues_api():
    my_issues = Issue.query.filter_by(user_id=current_user.id).all()

    summary = {
        "pending": Issue.query.filter_by(user_id=current_user.id, status="รอดำเนินการ").count(),
        "in_progress": Issue.query.filter_by(user_id=current_user.id, status="กำลังดำเนินการ").count(),
        "resolved": Issue.query.filter_by(user_id=current_user.id, status="แก้ไขแล้ว").count(),
    }

    issues_data = [
        {
            "id": i.id,
            "category": i.category,
            "detail": i.detail,
            "status": i.status,
            "urgency": i.urgency,   # 🔴 🟠 🟢
            "view": "ดูรายละเอียด"
        }
        for i in my_issues
    ]

    return jsonify({"summary": summary, "my_issues": issues_data})

# --- ฟอร์มเพิ่มปัญหาใหม่ ---
@issue_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_issue():
    if request.method == 'POST':
        category = request.form.get('category')
        detail = request.form.get('detail')
        location_text = request.form.get('location_text')
        location_link = request.form.get('location_link')
        urgency = request.form.get('urgency')

        if not category or not detail or not urgency:
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "error")
            return redirect(url_for('issue.new_issue'))

        new_issue = Issue(
            user_id=current_user.id,
            category=category,
            detail=detail,
            date_reported=date.today(),
            location_text=location_text,
            location_link=location_link,
            urgency=urgency
        )
        db.session.add(new_issue)
        db.session.commit()

        flash("บันทึกปัญหาเรียบร้อยแล้ว ✅", "success")
        return redirect(url_for('issue.list_issues'))

    return render_template('issue_form.html')
