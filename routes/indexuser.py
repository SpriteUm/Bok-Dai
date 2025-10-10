from flask import Blueprint, jsonify, session
from models.issue import Issue

indexuser_bp = Blueprint('indexuser', __name__)

@indexuser_bp.route('/api/issues', methods=['GET'])
def get_issues_dashboard():
    user_id = session.get('user_id')  # ต้องมีระบบ login ที่เก็บ user_id ใน session
    issues = Issue.query.filter_by(user_id=user_id).all() if user_id else []

    pending_count = sum(1 for i in issues if i.status == 'ยังไม่ดำเนินการ')
    in_progress_count = sum(1 for i in issues if i.status == 'กำลังดำเนินการ')
    resolved_count = sum(1 for i in issues if i.status == 'แก้ไขแล้ว')

    issue_list = []
    for issue in issues:
        urgency_color = {
            'สูง': 'red',
            'กลาง': 'orange',
            'ต่ำ': 'green'
        }.get(issue.urgency, 'gray')

        issue_list.append({
            "hud": issue.category,
            "detail": issue.detail,
            "status": issue.status,
            "urgency": urgency_color,
            "view": "รายละเอียด",
            "id": issue.id  # เพิ่ม id เพื่อใช้สร้างลิงก์
        })

    return jsonify({
        "summary": {
            "pending": pending_count,
            "in_progress": in_progress_count,
            "resolved": resolved_count
        },
        "my_issues": issue_list
    })