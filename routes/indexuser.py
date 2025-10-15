from datetime import datetime
import json
import os

from flask import Blueprint, jsonify, render_template, current_app, abort, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import text

from models.issue import Issue
from models import db
from models.issueStatusHistory import IssueStatusHistory
# optional: Notification model if you added it
try:
    from models.notification import Notification
except Exception:
    Notification = None

indexuser_bp = Blueprint('indexuser', __name__, template_folder='../templates')


@indexuser_bp.route('/', methods=['GET'])
@login_required
def indexuser():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    total_issues = in_progress_issues = resolved_issues = 0
    recent_issues = []
    pagination = None
    unread_notifications_count = 0

    # unread notifications count (if Notification model exists)
    if Notification is not None:
        try:
            unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, seen=False).count()
        except Exception:
            current_app.logger.exception("Failed counting unread notifications")

    try:
        # counts
        total_issues = Issue.query.filter_by(user_id=current_user.id, status='รอดำเนินการ').count()
        in_progress_issues = Issue.query.filter_by(user_id=current_user.id, status='กำลังดำเนินการ').count()
        resolved_issues = Issue.query.filter_by(user_id=current_user.id, status='แก้ไขแล้ว').count()

        # fetch issues with relationships if available
        orm_issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc())

        # pagination (simple)
        total_rows = orm_issues.count()
        pages = max(1, (total_rows + per_page - 1) // per_page)
        orm_issues = orm_issues.limit(per_page).offset((page - 1) * per_page).all()

        for it in orm_issues:
            # prepare status_history list (map to minimal dicts)
            sh_list = []
            try:
                hist = getattr(it, 'status_history', None) or []
                for h in sorted(hist, key=lambda x: getattr(x, 'timestamp', getattr(x, 'created_at', None) or datetime.min), reverse=True):
                    sh_list.append({
                        "id": getattr(h, "id", None),
                        "status": getattr(h, "status", None),
                        "notes": getattr(h, "notes", None),
                        "timestamp": getattr(h, "timestamp", getattr(h, "created_at", None)),
                        "response_image": getattr(h, "response_image", None),
                        "changer": {
                            "id": getattr(h, "changed_by_id", None),
                            "username": getattr(getattr(h, "changer", None), "username", None)
                        }
                    })
            except Exception:
                sh_list = []

            recent_issues.append({
                "id": it.id,
                "category": getattr(it, "category", "-") or "-",
                "detail": getattr(it, "detail", "-") or "-",
                "status": getattr(it, "status", "รอดำเนินการ") or "รอดำเนินการ",
                "urgency": getattr(it, "urgency", "") or "",
                "date_reported": getattr(it, "date_reported", None),
                "created_at": getattr(it, "created_at", None),
                "location_text": getattr(it, "location_text", "") or "",
                "location_link": getattr(it, "location_link", "") or "",
                # pass the mapped history so template can read latest notes/response_image
                "status_history": sh_list
            })

        # simple pagination object to reuse in template
        class SimplePagination:
            def __init__(self, page, per_page, total):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = max(1, (total + per_page - 1) // per_page)
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None

            def iter_pages(self, left_edge=1, right_edge=1, left_current=2, right_current=2):
                last = 0
                for num in range(1, self.pages + 1):
                    if num <= left_edge or \
                       (num > self.page - left_current - 1 and num < self.page + right_current) or \
                       num > self.pages - right_edge:
                        if last + 1 != num:
                            yield None
                        yield num
                        last = num

        pagination = SimplePagination(page, per_page, total_rows)

    except Exception as e:
        current_app.logger.warning("ORM query failed in indexuser(), falling back to raw SQL: %s", e)

        sql = text("""
            SELECT id, category, detail, date_reported, status, urgency, created_at, location_text, location_link
            FROM issues
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        try:
            rows = db.session.execute(sql, {"uid": current_user.id, "limit": per_page, "offset": (page - 1) * per_page}).mappings().all()
        except Exception as e2:
            current_app.logger.exception("Raw SQL failed in indexuser(): %s", e2)
            rows = []

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

            # fetch latest history for this issue to show preview
            sh_list = []
            try:
                hist_rows = db.session.execute(
                    text("SELECT id, status, notes, timestamp, response_image, changed_by_id FROM issue_status_history WHERE issue_id = :iid ORDER BY timestamp DESC LIMIT 5"),
                    {"iid": row.get('id')}
                ).mappings().all()
                for h in hist_rows:
                    sh_list.append({
                        "id": h.get('id'),
                        "status": h.get('status'),
                        "notes": h.get('notes'),
                        "timestamp": h.get('timestamp'),
                        "response_image": h.get('response_image'),
                        "changer": {"id": h.get('changed_by_id'), "username": None}
                    })
            except Exception:
                sh_list = []

            recent_issues.append({
                "id": row.get('id'),
                "category": row.get('category') or "-",
                "detail": row.get('detail') or "-",
                "status": status,
                "urgency": urgency,
                "date_reported": row.get('date_reported'),
                "created_at": row.get('created_at'),
                "location_text": row.get('location_text') or '',
                "location_link": row.get('location_link') or '',
                "status_history": sh_list
            })

        total_rows = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE user_id = :uid"), {"uid": current_user.id}).scalar() or 0
        total_issues = sum(1 for i in recent_issues if i["status"] == 'รอดำเนินการ')
        in_progress_issues = sum(1 for i in recent_issues if i["status"] == 'กำลังดำเนินการ')
        resolved_issues = sum(1 for i in recent_issues if i["status"] == 'แก้ไขแล้ว')

        class SimplePagination:
            def __init__(self, page, per_page, total):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = max(1, (total + per_page - 1) // per_page)
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None

            def iter_pages(self, left_edge=1, right_edge=1, left_current=2, right_current=2):
                last = 0
                for num in range(1, self.pages + 1):
                    if num <= left_edge or \
                       (num > self.page - left_current - 1 and num < self.page + right_current) or \
                       num > self.pages - right_edge:
                        if last + 1 != num:
                            yield None
                        yield num
                        last = num

        pagination = SimplePagination(page, per_page, total_rows)

    # render template with unread_notifications_count included
    return render_template(
        'indexuser.html',
        total_issues=total_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        recent_issues=recent_issues,
        pagination=pagination,
        unread_notifications_count=unread_notifications_count
    )


@indexuser_bp.route('/issue/<int:issue_id>', methods=['GET'])
@login_required
def view_issue(issue_id):
    # ensure user only sees their own issues
    issue = Issue.query.filter_by(id=issue_id, user_id=current_user.id).first()
    if not issue:
        abort(404)

    # collect image URLs for template (relationship or stored filenames)
    images = []
    try:
        for img in getattr(issue, 'images', []) or []:
            filename = getattr(img, 'filename', None)
            if filename:
                images.append(url_for('static', filename=f'uploads/{filename}'))
    except Exception:
        images = []

    # prepare status_history in a safe form for template (list of objects/dicts)
    status_history = []
    try:
        hist = getattr(issue, 'status_history', None) or []
        for h in sorted(hist, key=lambda x: getattr(x, 'timestamp', getattr(x, 'created_at', None) or datetime.min), reverse=True):
            status_history.append(h)
    except Exception:
        status_history = []

    # pass the model objects where template expects attributes (issue.status_history used)
    # but also prepare a safe lightweight dict if you prefer
    # include location_link fallback
    if not hasattr(issue, 'location_link'):
        issue.location_link = ''

    return render_template('view_issue.html', issue=issue, images=images, status_history=status_history)


@indexuser_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    if Notification is None:
        abort(404)
    try:
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(100).all()
    except Exception:
        current_app.logger.exception("Failed loading notifications")
        notifs = []
    return render_template('notifications.html', notifications=notifs)
