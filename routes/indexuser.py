from datetime import datetime
import json

from flask import Blueprint, render_template, current_app, abort, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import text

from models.issue import Issue
from models import db

indexuser_bp = Blueprint('indexuser', __name__, template_folder='../templates')

def _import_optional(name_camel='issueStatusHistory', name_snake='issue_status_history'):
    try:
        module = __import__(f"models.{name_camel}", fromlist=[name_camel])
        return module
    except Exception:
        try:
            module = __import__(f"models.{name_snake}", fromlist=[name_snake])
            return module
        except Exception:
            return None

@indexuser_bp.route('/', methods=['GET'])
@login_required
def indexuser():
    notif_mod = _import_optional('notification', 'notification')
    IssueStatusHistoryMod = _import_optional('issueStatusHistory', 'issue_status_history')

    Notification = None
    if notif_mod:
        try:
            Notification = getattr(notif_mod, 'Notification', None)
        except Exception:
            Notification = None

    IssueStatusHistory = None
    if IssueStatusHistoryMod:
        try:
            IssueStatusHistory = getattr(IssueStatusHistoryMod, 'IssueStatusHistory', None)
        except Exception:
            IssueStatusHistory = None

    page = request.args.get('page', 1, type=int)
    per_page = 20

    total_issues = in_progress_issues = resolved_issues = 0
    recent_issues = []
    pagination = None
    unread_notifications_count = 0

    if Notification is not None:
        try:
            unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, seen=False).count()
        except Exception:
            current_app.logger.exception("Failed counting unread notifications")

    try:
        total_issues = Issue.query.filter_by(user_id=current_user.id, status='รอดำเนินการ').count()
        in_progress_issues = Issue.query.filter_by(user_id=current_user.id, status='กำลังดำเนินการ').count()
        resolved_issues = Issue.query.filter_by(user_id=current_user.id, status='แก้ไขแล้ว').count()

        orm_issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc())

        total_rows = orm_issues.count()
        orm_issues = orm_issues.limit(per_page).offset((page - 1) * per_page).all()

        # Inspect status-history and issues table columns once per request
        try:
            status_col_info = db.session.execute(text("PRAGMA table_info('issue_status_history')")).mappings().all()
            status_cols = {r['name'] for r in status_col_info}
        except Exception:
            status_cols = set()

        try:
            issue_col_info = db.session.execute(text("PRAGMA table_info('issues')")).mappings().all()
            issue_cols = {r['name'] for r in issue_col_info}
        except Exception:
            issue_cols = set()

        for it in orm_issues:
            sh_list = []
            try:
                select_cols = [
                    "id",
                    "status",
                    ("note AS notes" if 'note' in status_cols else ("notes AS notes" if 'notes' in status_cols else "NULL AS notes")),
                    ("timestamp" if 'timestamp' in status_cols else ("created_at AS timestamp" if 'created_at' in status_cols else "NULL AS timestamp")),
                    ("response_id AS response_image" if 'response_id' in status_cols else ("response_image AS response_image" if 'response_image' in status_cols else "NULL AS response_image")),
                    ("chang_id AS changed_by_id" if 'chang_id' in status_cols else ("changed_by_id AS changed_by_id" if 'changed_by_id' in status_cols else ("changer_id AS changed_by_id" if 'changer_id' in status_cols else "NULL AS changed_by_id")))
                ]
                sql = f"SELECT {', '.join(select_cols)} FROM issue_status_history WHERE issue_id = :iid ORDER BY timestamp DESC LIMIT 5"
                rows = db.session.execute(text(sql), {"iid": it.id}).mappings().all()
                for h in rows:
                    resp_img = h.get('response_image')
                    resp_img_url = None
                    if resp_img:
                        try:
                            ts = h.get('timestamp')
                            if ts and hasattr(ts, "timestamp"):
                                resp_img_url = url_for('static', filename='uploads/' + resp_img) + f"?v={int(ts.timestamp())}"
                            else:
                                resp_img_url = url_for('static', filename='uploads/' + resp_img)
                        except Exception:
                            resp_img_url = resp_img
                    sh_list.append({
                        "id": h.get('id'),
                        "status": h.get('status'),
                        "notes": h.get('notes'),
                        "timestamp": h.get('timestamp'),
                        "response_image": resp_img,
                        "response_image_url": resp_img_url,
                        "changer": {"id": h.get('changed_by_id'), "username": None}
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
                "status_history": sh_list
            })

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

        try:
            col_info_issues = db.session.execute(text("PRAGMA table_info('issues')")).mappings().all()
            issue_cols = {r['name'] for r in col_info_issues}
        except Exception:
            issue_cols = set()

        select_cols = ["id", "category", "detail", "date_reported", "status", "urgency", "created_at"]
        if 'location_text' in issue_cols:
            select_cols.append("location_text")
        else:
            select_cols.append("'' AS location_text")
        if 'location_link' in issue_cols:
            select_cols.append("location_link")
        else:
            select_cols.append("'' AS location_link")

        sql = text(f"""
            SELECT {', '.join(select_cols)}
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

            sh_list = []
            try:
                hist_rows = db.session.execute(text(
                    "SELECT id, status, note AS notes, timestamp, response_id AS response_image, chang_id AS changed_by_id "
                    "FROM issue_status_history WHERE issue_id = :iid ORDER BY timestamp DESC LIMIT 5"
                ), {"iid": row.get('id')}).mappings().all()
                for h in hist_rows:
                    resp_img = h.get('response_image')
                    resp_img_url = None
                    if resp_img:
                        try:
                            ts = h.get('timestamp')
                            if ts and hasattr(ts, "timestamp"):
                                resp_img_url = url_for('static', filename='uploads/' + resp_img) + f"?v={int(ts.timestamp())}"
                            else:
                                resp_img_url = url_for('static', filename='uploads/' + resp_img)
                        except Exception:
                            resp_img_url = resp_img
                    sh_list.append({
                        "id": h.get('id'),
                        "status": h.get('status'),
                        "notes": h.get('notes'),
                        "timestamp": h.get('timestamp'),
                        "response_image": resp_img,
                        "response_image_url": resp_img_url,
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
    issue = Issue.query.filter_by(id=issue_id, user_id=current_user.id).first()
    if not issue:
        abort(404)

    images = []
    try:
        for img in getattr(issue, 'images', []) or []:
            filename = getattr(img, 'filename', None)
            if filename:
                images.append(url_for('static', filename=f'uploads/{filename}'))
    except Exception:
        images = []

    try:
        col_info = db.session.execute(text("PRAGMA table_info('issue_status_history')")).mappings().all()
        cols = {r['name'] for r in col_info}
    except Exception:
        cols = set()

    select_cols = [
        "id",
        "status",
        ("note AS notes" if 'note' in cols else ("notes AS notes" if 'notes' in cols else "NULL AS notes")),
        ("timestamp" if 'timestamp' in cols else ("created_at AS timestamp" if 'created_at' in cols else "NULL AS timestamp")),
        ("response_id AS response_image" if 'response_id' in cols else ("response_image AS response_image" if 'response_image' in cols else "NULL AS response_image")),
        ("chang_id AS changed_by_id" if 'chang_id' in cols else ("changed_by_id AS changed_by_id" if 'changed_by_id' in cols else ("changer_id AS changed_by_id" if 'changer_id' in cols else "NULL AS changed_by_id")))
    ]
    try:
        rows = db.session.execute(text(f"SELECT {', '.join(select_cols)} FROM issue_status_history WHERE issue_id = :iid ORDER BY timestamp DESC"), {"iid": issue.id}).mappings().all()
    except Exception:
        rows = []

    status_history = []
    for h in rows:
        resp_img = h.get('response_image')
        resp_img_url = None
        if resp_img:
            try:
                ts = h.get('timestamp')
                if ts and hasattr(ts, "timestamp"):
                    resp_img_url = url_for('static', filename='uploads/' + resp_img) + f"?v={int(ts.timestamp())}"
                else:
                    resp_img_url = url_for('static', filename='uploads/' + resp_img)
            except Exception:
                resp_img_url = resp_img
        status_history.append({
            "id": h.get('id'),
            "status": h.get('status'),
            "notes": h.get('notes'),
            "timestamp": h.get('timestamp'),
            "response_image": resp_img,
            "response_image_url": resp_img_url,
            "changer_username": None
        })

    issue_data = {
        "id": issue.id,
        "category": issue.category or "-",
        "detail": issue.detail or "-",
        "status": issue.status or "รอดำเนินการ",
        "urgency": issue.urgency or "",
        "date_reported": issue.date_reported,
        "location_link": getattr(issue, "location_link", "") or "",
        "status_history": status_history
    }

    return render_template('view_issue.html', issue=issue_data, images=images)

@indexuser_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    notif_mod = _import_optional('notification', 'notification')
    if not notif_mod:
        abort(404)
    Notification = getattr(notif_mod, 'Notification', None)
    if Notification is None:
        abort(404)
    try:
        notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(100).all()
    except Exception:
        current_app.logger.exception("Failed loading notifications")
        notifs = []
    return render_template('notifications.html', notifications=notifs)
