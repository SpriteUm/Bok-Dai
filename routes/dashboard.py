from flask import Blueprint, jsonify
from models.issue import Issue

indexuser_bp = Blueprint('indexuser', __name__)

@indexuser_bp.route('/api/issues', methods=['GET'])
def get_issues():
    issues = Issue.query.all()

    issue_list = []
    for issue in issues:
        issue_list.append({
            "id": issue.id,
            "category": issue.category,
            "detail": issue.detail,
            "date": issue.date_reported.strftime('%Y-%m-%d'),
            "status": issue.status
        })

    return jsonify(issue_list)