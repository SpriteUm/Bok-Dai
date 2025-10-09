# 1. Standard library imports
from datetime import datetime, date
from functools import wraps
import json

# 2. Third-party imports
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from sqlalchemy import func, or_

# 3. Local application imports
from models import db
from models.user import User
from models.issue import Issue
from models.issueStatusHistory import IssueStatusHistory

# --- Blueprint Setup ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Helper Function (Decorator) ---
def admin_required(f):
    """Decorator for checking if the current user is an 'admin'."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard & Main Page Routes ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """แสดงหน้าแดชบอร์ดหลักของ Admin พร้อมข้อมูลสรุปทั้งหมด"""
    
    total_issues = Issue.query.count()
    issues_pending = Issue.query.filter_by(status='รอดำเนินการ').count()
    issues_in_progress = Issue.query.filter_by(status='กำลังดำเนินการ').count()
    issues_completed = Issue.query.filter_by(status='แก้ไขแล้ว').count()
    today_start = datetime.combine(date.today(), datetime.min.time())
    issues_today = Issue.query.filter(Issue.created_at >= today_start).count()
    issues_urgent = Issue.query.filter_by(urgency='🔴').count()
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(5).all()

    chart_data_query = db.session.query(
        Issue.category, 
        func.count(Issue.id)
    ).group_by(Issue.category).order_by(func.count(Issue.id).desc()).limit(5).all()
    
    chart_labels = [row[0] for row in chart_data_query]
    chart_values = [row[1] for row in chart_data_query]
    
    chart_data = { "labels": chart_labels, "values": chart_values }

    return render_template('admin.html',
                           total_issues=total_issues,
                           issues_pending=issues_pending,
                           issues_in_progress=issues_in_progress,
                           issues_completed=issues_completed,
                           issues_today=issues_today,
                           issues_urgent=issues_urgent,
                           recent_issues=recent_issues,
                           chart_data=chart_data
                          )

# --- Issue Management Routes ---
@admin_bp.route('/issues')
@admin_required
def manage_issues():
    """แสดงรายการปัญหาทั้งหมด พร้อมระบบค้นหา, กรอง, จัดเรียง และแบ่งหน้า"""
    
    # --- 1. รับค่าจาก URL (GET parameters) ---
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')
    filter_status = request.args.get('status', '')
    filter_urgency = request.args.get('urgency', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    # --- 2. สร้าง Query เริ่มต้น ---
    query = Issue.query.join(User)

    # --- 3. เพิ่มเงื่อนไขการกรอง (Filter) ---
    if search_term:
        search_like = f'%{search_term}%'
        query = query.filter(
            or_(
                Issue.detail.ilike(search_like),
                Issue.category.ilike(search_like),
                User.username.ilike(search_like)
            )
        )
    if filter_status:
        query = query.filter(Issue.status == filter_status)
    if filter_urgency:
        query = query.filter(Issue.urgency == filter_urgency)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        query = query.filter(Issue.date_reported >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        query = query.filter(Issue.date_reported <= end_date)

    # --- 4. เพิ่มเงื่อนไขการจัดเรียง (Sort) ---
    sort_column_map = {
        'category': Issue.category,
        'date_reported': Issue.date_reported,
        'status': Issue.status
    }
    sort_column = sort_column_map.get(sort_by, Issue.created_at)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # --- 5. ดึงข้อมูลแบบแบ่งหน้า (Paginate) ---
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    issues = pagination.items

    # --- 6. ส่งข้อมูลกลับไปที่ Template ---
    return render_template('reportadmin.html', 
                           issues=issues,
                           pagination=pagination,
                           issue_statuses=Issue.ALLOWED_STATUSES,
                           search_term=search_term,
                           filter_status=filter_status,
                           filter_urgency=filter_urgency,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           sort_by=sort_by,
                           sort_order=sort_order
                          )

# ... (โค้ดส่วนที่เหลือของไฟล์เหมือนเดิม) ...
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
    if not new_status or new_status not in Issue.ALLOWED_STATUSES:
        flash('สถานะที่ส่งมาไม่ถูกต้อง', 'error')
    else:
        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        history_log = IssueStatusHistory(
            issue_id=issue.id, status=new_status, notes=notes,
            changed_by_id=current_user.id
        )
        db.session.add(history_log)
        db.session.commit()
        flash(f'สถานะของรายงาน #{issue.id} ถูกอัปเดตเป็น "{new_status}" แล้ว', 'success')
    return redirect(url_for('admin.update_issue_page', issue_id=issue.id))

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('indexuser.html', users=users)