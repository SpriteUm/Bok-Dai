from flask import Blueprint, jsonify, render_template
from models.issue import Issue
from flask_login import login_required


indexuser_bp = Blueprint('indexuser', __name__)

@indexuser_bp.route('/indexuser')
@login_required
def indexuser():
    return render_template('indexuser.html')

@indexuser_bp.route('/api/issues', methods=['GET'])
def get_issues():
    issues = Issue.query.all()
    issue_list = []

    for issue in issues:
        urgency_color = {
            '🔴': 'red',
            '🟠': 'orange',
            '🟢': 'green'
        }.get(issue.urgency, 'gray')

        date_str = issue.date_reported.strftime('%Y-%m-%d') if issue.date_reported else '-'

        issue_list.append({
            "id": issue.id,
            "category": issue.category or "-",
            "detail": issue.detail or "-",
            "date": date_str,
            "status": issue.status or "รอดำเนินการ",
            "urgency": urgency_color,
            "view": "รายละเอียด"
        })

    return jsonify({
        "summary": {
            "total": len(issues),
            "pending": sum(1 for i in issues if i.status == 'รอดำเนินการ'),
            "in_progress": sum(1 for i in issues if i.status == 'กำลังดำเนินการ'),
            "resolved": sum(1 for i in issues if i.status == 'แก้ไขแล้ว')
        },
        "my_issues": issue_list
    })