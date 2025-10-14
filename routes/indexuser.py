from flask import Blueprint, jsonify, render_template, current_app, abort, url_for
from flask_login import login_required, current_user
from models.issue import Issue
from models import db
from sqlalchemy import text

indexuser_bp = Blueprint('indexuser', __name__, template_folder='../templates')

@indexuser_bp.route('/', methods=['GET'])
@login_required
def indexuser():
    total_issues = in_progress_issues = resolved_issues = 0
    recent_issues = []

    try:
        total_issues = Issue.query.filter_by(user_id=current_user.id, status='รอดำเนินการ').count()
        in_progress_issues = Issue.query.filter_by(user_id=current_user.id, status='กำลังดำเนินการ').count()
        resolved_issues = Issue.query.filter_by(user_id=current_user.id, status='แก้ไขแล้ว').count()

        orm_issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc()).all()

        for it in orm_issues:
            recent_issues.append({
                "id": it.id,
                "category": getattr(it, "category", "-") or "-",
                "detail": getattr(it, "detail", "-") or "-",
                "status": getattr(it, "status", "รอดำเนินการ") or "รอดำเนินการ",
                "urgency": getattr(it, "urgency", "") or ""
            })

    except Exception as e:
        current_app.logger.warning("ORM query failed in indexuser(), falling back to raw SQL: %s", e)

        sql = text("""
            SELECT id, category, detail, date_reported, status, urgency, created_at
            FROM issues
            WHERE user_id = :uid
            ORDER BY created_at DESC
        """)
        rows = db.session.execute(sql, {"uid": current_user.id}).mappings().all()

        for row in rows:
            status = row.get('status') or 'รอดำเนินการ'
            urgency_raw = (row.get('urgency') or '')
            if urgency_raw in ('🔴', 'red'):
                urgency = '🔴'
            elif urgency_raw in ('🟠', 'orange'):
                urgency = '🟠'
            elif urgency_raw in ('🟢', 'green'):
                urgency = '🟢'
            else:
                urgency = ''

            recent_issues.append({
                "id": row.get('id'),
                "category": row.get('category') or "-",
                "detail": row.get('detail') or "-",
                "status": status,
                "urgency": urgency
            })

        total_issues = sum(1 for i in recent_issues if i["status"] == 'รอดำเนินการ')
        in_progress_issues = sum(1 for i in recent_issues if i["status"] == 'กำลังดำเนินการ')
        resolved_issues = sum(1 for i in recent_issues if i["status"] == 'แก้ไขแล้ว')

    return render_template(
        'indexuser.html',
        total_issues=total_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        recent_issues=recent_issues
    )

@indexuser_bp.route('/issue/<int:issue_id>', methods=['GET'])
@login_required
def view_issue(issue_id):
    # เอาเฉพาะ issue ของผู้ใช้ปัจจุบันเท่านั้นเพื่อความปลอดภัย
    issue = Issue.query.filter_by(id=issue_id, user_id=current_user.id).first()
    if not issue:
        abort(404)

    # เตรียมข้อมูลรูปภาพถ้ามี (Issue.images เป็น relationship ถ้ามี)
    images = []
    try:
        for img in getattr(issue, 'images', []) or []:
            # ถ้าเก็บ filename ใน IssueImage, สร้าง path สำหรับเทมเพลต
            images.append(url_for('static', filename=f'uploads/{getattr(img, "filename", "")}'))
    except Exception:
        images = []

    # ส่งข้อมูล issue ไปยังเทมเพลต (ใช้ attributes จาก ORM ถ้าเป็นไปได้)
    issue_data = {
        "id": issue.id,
        "category": getattr(issue, "category", "-") or "-",
        "detail": getattr(issue, "detail", "-") or "-",
        "status": getattr(issue, "status", "รอดำเนินการ") or "รอดำเนินการ",
        "urgency": getattr(issue, "urgency", "") or "",
        "date_reported": getattr(issue, "date_reported", None)
    }

    return render_template('view_issue.html', issue=issue_data, images=images)
