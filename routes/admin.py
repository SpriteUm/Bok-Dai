from datetime import datetime, date
from functools import wraps
import json

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, text

from models import db
from models.user import User
from models.issue import Issue
from models.issueStatusHistory import IssueStatusHistory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_issues = issues_pending = issues_in_progress = issues_completed = issues_today = issues_urgent = 0
    recent_issues = []
    chart_data = {"labels": [], "values": []}
    hotspot_data = []

    try:
        # ORM path (preferred)
        total_issues = Issue.query.count()
        issues_pending = Issue.query.filter_by(status='รอดำเนินการ').count()
        issues_in_progress = Issue.query.filter_by(status='กำลังดำเนินการ').count()
        issues_completed = Issue.query.filter_by(status='แก้ไขแล้ว').count()
        today_start = datetime.combine(date.today(), datetime.min.time())
        issues_today = Issue.query.filter(Issue.created_at >= today_start).count()
        issues_urgent = Issue.query.filter_by(urgency='🔴').count()

        orm_recent = Issue.query.order_by(Issue.created_at.desc()).limit(30).all()
        for it in orm_recent:
            created = getattr(it, "created_at", None)
            date_reported = created.strftime('%Y-%m-%d') if hasattr(created, 'strftime') else (str(created) if created else '')
            recent_issues.append({
                "id": it.id,
                "category": getattr(it, "category", "-") or "-",
                "detail": getattr(it, "detail", "-") or "-",
                "status": getattr(it, "status", "รอดำเนินการ") or "รอดำเนินการ",
                "urgency": getattr(it, "urgency", "") or "",
                "date_reported": date_reported,
                "created_at": created,
                # location_text may not exist in DB; use attribute if model provides it
                "location_text": getattr(it, "location_text", "") or "",
                "location_link": getattr(it, "location_link", "") or ""
            })

        chart_rows = db.session.query(Issue.category, func.count(Issue.id)) \
            .group_by(Issue.category).order_by(func.count(Issue.id).desc()).limit(5).all()
        chart_data = {"labels": [r[0] for r in chart_rows], "values": [r[1] for r in chart_rows]}

        hotspot_issues = Issue.query.filter(Issue.location_link.isnot(None), Issue.location_link != '') \
            .order_by(Issue.created_at.desc()).limit(30).all()
        for issue in hotspot_issues:
            try:
                loc = issue.location_link or ''
                if '@' in loc:
                    coords_part = loc.split('@')[1].split(',')[0:2]
                    lat = float(coords_part[0]); lng = float(coords_part[1])
                    hotspot_data.append({
                        'lat': lat,
                        'lng': lng,
                        'category': issue.category,
                        'urgency': issue.urgency,
                        'issue_id': issue.id,
                        'location_link': issue.location_link or ''
                    })
            except (IndexError, ValueError, TypeError):
                continue

    except Exception as e:
        # Fallback raw SQL path if ORM fails (eg. Enum LookupError)
        current_app.logger.warning("ORM failed in admin.dashboard, falling back to raw SQL: %s", e)
        try:
            total_issues = db.session.execute(text("SELECT COUNT(*) FROM issues")).scalar() or 0
            issues_pending = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE status = :s"), {"s": "รอดำเนินการ"}).scalar() or 0
            issues_in_progress = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE status = :s"), {"s": "กำลังดำเนินการ"}).scalar() or 0
            issues_completed = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE status = :s"), {"s": "แก้ไขแล้ว"}).scalar() or 0
            issues_today = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE created_at >= :t"), {"t": datetime.combine(date.today(), datetime.min.time())}).scalar() or 0
            issues_urgent = db.session.execute(text("SELECT COUNT(*) FROM issues WHERE urgency = :u"), {"u": "🔴"}).scalar() or 0
        except Exception:
            pass

        try:
            # removed i.location_text to avoid "no such column"
            sql = text("SELECT id, category, detail, status, urgency, created_at, location_link FROM issues ORDER BY created_at DESC LIMIT 30")
            rows = db.session.execute(sql).mappings().all()
            for row in rows:
                created = row.get('created_at')
                if hasattr(created, 'strftime'):
                    date_reported = created.strftime('%Y-%m-%d')
                else:
                    date_reported = str(created) if created else ''
                status = row.get('status') or 'รอดำเนินการ'
                urgency_raw = row.get('urgency') or ''
                urgency_display = '🔴' if urgency_raw in ('🔴','red') else ('🟠' if urgency_raw in ('🟠','orange') else ('🟢' if urgency_raw in ('🟢','green') else ''))
                recent_issues.append({
                    "id": row.get('id'),
                    "category": row.get('category') or "-",
                    "detail": row.get('detail') or "-",
                    "status": status,
                    "urgency": urgency_display,
                    "date_reported": date_reported,
                    "created_at": created,
                    # no location_text column in SQL: fill safely
                    "location_text": row.get('location_text') or '',
                    "location_link": row.get('location_link') or ''
                })

            chart_rows = db.session.execute(text("SELECT category, COUNT(id) as cnt FROM issues GROUP BY category ORDER BY cnt DESC LIMIT 5")).mappings().all()
            chart_data = {"labels": [r['category'] for r in chart_rows], "values": [r['cnt'] for r in chart_rows]}

            hotspot_rows = db.session.execute(text("SELECT id, category, urgency, location_link FROM issues WHERE location_link IS NOT NULL AND location_link != '' ORDER BY created_at DESC LIMIT 30")).mappings().all()
            for row in hotspot_rows:
                try:
                    loc = row.get('location_link') or ''
                    if '@' in loc:
                        coords_part = loc.split('@')[1].split(',')[0:2]
                        lat = float(coords_part[0]); lng = float(coords_part[1])
                        hotspot_data.append({
                            'lat': lat,
                            'lng': lng,
                            'category': row.get('category'),
                            'urgency': row.get('urgency'),
                            'issue_id': row.get('id'),
                            'location_link': row.get('location_link') or ''
                        })
                except (IndexError, ValueError, TypeError):
                    continue
        except Exception as e2:
            current_app.logger.error("Raw SQL fallback in dashboard also failed: %s", e2)

    return render_template('admin.html',
                           total_issues=total_issues or 0,
                           issues_pending=issues_pending or 0,
                           issues_in_progress=issues_in_progress or 0,
                           issues_completed=issues_completed or 0,
                           issues_today=issues_today or 0,
                           issues_urgent=issues_urgent or 0,
                           recent_issues=recent_issues,
                           chart_data=chart_data,
                           hotspot_data=json.dumps(hotspot_data)
                          )

@admin_bp.route('/issues')
@admin_required
def manage_issues():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search_term = request.args.get('search', '').strip()
    filter_status = request.args.get('status', '').strip()
    filter_urgency = request.args.get('urgency', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # Build WHERE clauses and params for raw SQL (join users)
    where_clauses = ["1=1"]
    params = {}

    if search_term:
        where_clauses.append("(i.detail LIKE :search OR i.category LIKE :search OR u.username LIKE :search)")
        params['search'] = f"%{search_term}%"
    if filter_status:
        where_clauses.append("i.status = :status")
        params['status'] = filter_status
    if filter_urgency:
        where_clauses.append("i.urgency = :urgency")
        params['urgency'] = filter_urgency
    # handle date filters: convert to plain YYYY-MM-DD strings and compare with DATE(...)
    if start_date_str:
        try:
            sd = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            where_clauses.append("DATE(i.date_reported) >= :start_date")
            params['start_date'] = sd.strftime('%Y-%m-%d')
        except ValueError:
            current_app.logger.warning("manage_issues: invalid start_date format: %s", start_date_str)
    if end_date_str:
        try:
            ed = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            where_clauses.append("DATE(i.date_reported) <= :end_date")
            params['end_date'] = ed.strftime('%Y-%m-%d')
        except ValueError:
            current_app.logger.warning("manage_issues: invalid end_date format: %s", end_date_str)

    allowed_sorts = {'category': 'i.category', 'date_reported': 'i.date_reported', 'status': 'i.status', 'created_at': 'i.created_at'}
    sort_col = allowed_sorts.get(sort_by, 'i.created_at')
    sort_dir = 'ASC' if sort_order == 'asc' else 'DESC'

    where_sql = " AND ".join(where_clauses)

    # total count
    count_sql = text(f"SELECT COUNT(*) FROM issues i LEFT JOIN users u ON u.id = i.user_id WHERE {where_sql}")
    try:
        total = db.session.execute(count_sql, params).scalar() or 0
    except Exception as e:
        current_app.logger.exception("Count query failed in manage_issues: %s", e)
        total = 0

    offset = (page - 1) * per_page

    data_sql = text(f"""
        SELECT
            i.id, i.category, i.detail, i.date_reported, i.status, i.urgency,
            i.location_link, i.created_at,
            u.id AS user_id, u.username
        FROM issues i
        LEFT JOIN users u ON u.id = i.user_id
        WHERE {where_sql}
        ORDER BY {sort_col} {sort_dir}
        LIMIT :limit OFFSET :offset
    """)
    params.update({"limit": per_page, "offset": offset})

    # --- Improved data fetch with debug and fallback ---
    issues = []
    try:
        rows = db.session.execute(data_sql, params).mappings().all()
        current_app.logger.debug("manage_issues: fetched rows count=%s params=%s", len(rows), params)
        if len(rows) == 0 and total > 0:
            current_app.logger.warning("manage_issues: zero rows returned but total=%s; where_sql=%s params=%s", total, where_sql, params)

        for r in rows:
            created = r.get('created_at')
            dr = r.get('date_reported')
            if dr is None:
                if hasattr(created, 'strftime'):
                    date_reported = created.strftime('%Y-%m-%d')
                else:
                    date_reported = str(created) if created else ''
            else:
                date_reported = dr.strftime('%Y-%m-%d') if hasattr(dr, 'strftime') else str(dr)

            issues.append({
                "id": r.get('id'),
                "category": r.get('category') or "-",
                "detail": r.get('detail') or "-",
                "date_reported": date_reported,
                "status": r.get('status') or 'รอดำเนินการ',
                "urgency": r.get('urgency') or '',
                "location_text": r.get('location_text') or '',
                "location_link": r.get('location_link') or '',
                "created_at": created,
                "user": {
                    "id": r.get('user_id'),
                    "username": r.get('username') or '—'
                }
            })
    except Exception as e:
        current_app.logger.exception("Data query failed in manage_issues: %s -- will attempt simple fallback", e)
        # fallback: try a simpler query without filters to validate DB connectivity
        try:
            fallback_sql = text("""
                SELECT i.id, i.category, i.detail, i.date_reported, i.status, i.urgency,
                       i.location_link, i.created_at,
                       u.id AS user_id, u.username
                FROM issues i
                LEFT JOIN users u ON u.id = i.user_id
                ORDER BY i.created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            fb_params = {"limit": per_page, "offset": offset}
            fb_rows = db.session.execute(fallback_sql, fb_params).mappings().all()
            current_app.logger.debug("manage_issues fallback rows count=%s", len(fb_rows))
            for r in fb_rows:
                created = r.get('created_at')
                dr = r.get('date_reported')
                if dr is None:
                    if hasattr(created, 'strftime'):
                        date_reported = created.strftime('%Y-%m-%d')
                    else:
                        date_reported = str(created) if created else ''
                else:
                    date_reported = dr.strftime('%Y-%m-%d') if hasattr(dr, 'strftime') else str(dr)

                issues.append({
                    "id": r.get('id'),
                    "category": r.get('category') or "-",
                    "detail": r.get('detail') or "-",
                    "date_reported": date_reported,
                    "status": r.get('status') or 'รอดำเนินการ',
                    "urgency": r.get('urgency') or '',
                    "location_text": r.get('location_text') or '',
                    "location_link": r.get('location_link') or '',
                    "created_at": created,
                    "user": {
                        "id": r.get('user_id'),
                        "username": r.get('username') or '—'
                    }
                })
        except Exception as e2:
            current_app.logger.exception("Fallback data query also failed in manage_issues: %s", e2)
            issues = []

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

    pagination = SimplePagination(page, per_page, total)

    return render_template('reportadmin.html',
                           issues=issues,
                           pagination=pagination,
                           issue_statuses=getattr(Issue, "ALLOWED_STATUSES", []),
                           search_term=search_term,
                           filter_status=filter_status,
                           filter_urgency=filter_urgency,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           sort_by=sort_by,
                           sort_order=sort_order
                          )

@admin_bp.route('/issue/update/<int:issue_id>', methods=['GET', 'POST'])
@admin_required
def update_issue_page(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if request.method == 'POST':
        issue.detail = request.form.get('detail', issue.detail)
        db.session.commit()
        flash(f'อัปเดตรายละเอียดของ Issue #{issue.id} เรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin.update_issue_page', issue_id=issue.id))
    return render_template('updateadmin.html', issue=issue)

@admin_bp.route('/issue/update_status/<int:issue_id>', methods=['POST'])
@admin_required
def update_issue_status(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '').strip()
    allowed = getattr(Issue, "ALLOWED_STATUSES", [])
    if not new_status or new_status not in allowed:
        flash('สถานะที่ส่งมาไม่ถูกต้อง', 'error')
    else:
        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        history_log = IssueStatusHistory(issue_id=issue.id, status=new_status, notes=notes, changed_by_id=current_user.id)
        db.session.add(history_log)
        db.session.commit()
        flash(f'สถานะของรายงาน #{issue.id} ถูกอัปเดตเป็น "{new_status}" แล้ว', 'success')
    return redirect(url_for('admin.update_issue_page', issue_id=issue.id))

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin_users.html', users=users)
