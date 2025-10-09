# 1. Standard library imports
from datetime import datetime, date
from functools import wraps

# 2. Third-party imports
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

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
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard & Main Page Routes ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """แสดงหน้าแดชบอร์ดหลักของ Admin พร้อมข้อมูลสรุปทั้งหมด"""
    
    # --- ดึงข้อมูลสำหรับ Summary Cards ---
    total_issues = Issue.query.count()
    issues_pending = Issue.query.filter_by(status='รอดำเนินการ').count()
    issues_in_progress = Issue.query.filter_by(status='กำลังดำเนินการ').count()
    issues_completed = Issue.query.filter_by(status='แก้ไขแล้ว').count()
    
    # คำนวณหาปัญหาวันนี้
    today_start = datetime.combine(date.today(), datetime.min.time())
    issues_today = Issue.query.filter(Issue.created_at >= today_start).count()
    
    # หาก urgency เก็บเป็น '🔴', '🟠', '🟢'
    issues_urgent = Issue.query.filter_by(urgency='🔴').count()
    
    # --- ดึงข้อมูลสำหรับตาราง "ปัญหาล่าสุด" ---
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(5).all()

    return render_template('admin.html',
                           total_issues=total_issues,
                           issues_pending=issues_pending,
                           issues_in_progress=issues_in_progress,
                           issues_completed=issues_completed,
                           issues_today=issues_today,
                           issues_urgent=issues_urgent,
                           recent_issues=recent_issues)

# --- Issue Management Routes ---
@admin_bp.route('/issues')
@admin_required
def manage_issues():
    """แสดงรายการปัญหา/รายงานทั้งหมด"""
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    # **NOTE:** หน้านี้อาจจะเป็น report.html หรือ reportadmin.html ขึ้นอยู่กับไฟล์ของคุณ
    return render_template('report.html', issues=issues)


# --- ROUTE สำหรับ "หน้า" แก้ไขรายละเอียด ---
@admin_bp.route('/issue/update/<int:issue_id>', methods=['GET', 'POST'])
@admin_required
def update_issue_page(issue_id):
    """
    จัดการ "หน้า" สำหรับแก้ไขรายละเอียดของ Issue
    - GET: แสดงฟอร์มพร้อมข้อมูลเดิม
    - POST: รับข้อมูลจากฟอร์มใหญ่ (ที่อาจมีหลาย field) แล้วบันทึก
    """
    issue = Issue.query.get_or_404(issue_id)

    if request.method == 'POST':
        # ส่วนนี้จะทำงานเมื่อกดบันทึกจากฟอร์มในหน้า updateadmin.html
        # คุณสามารถเพิ่มการรับค่า field อื่นๆ ได้ที่นี่
        issue.detail = request.form.get('detail', issue.detail)
        # ...เพิ่ม field อื่นๆ ตามต้องการ...

        db.session.commit()
        flash(f'อัปเดตรายละเอียดของ Issue #{issue.id} เรียบร้อยแล้ว', 'success')
        return redirect(url_for('admin.update_issue_page', issue_id=issue.id))

    # สำหรับ GET request, แสดงหน้าฟอร์มแก้ไข
    return render_template('updateadmin.html', issue=issue)


# --- ROUTE สำหรับ "ฟอร์ม" อัปเดตสถานะ ---
@admin_bp.route('/issue/update_status/<int:issue_id>', methods=['POST'])
@admin_required
def update_issue_status(issue_id):
    """
    จัดการ "ฟอร์ม" อัปเดตสถานะโดยเฉพาะ (จากหน้า detail)
    บันทึกสถานะใหม่, สร้างประวัติ (Timeline), แล้วกลับไปหน้าเดิม
    """
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '').strip()

    if not new_status or new_status not in Issue.ALLOWED_STATUSES:
        flash('สถานะที่ส่งมาไม่ถูกต้อง', 'error')
    else:
        # อัปเดตสถานะของ Issue หลัก
        issue.status = new_status
        issue.updated_at = datetime.utcnow()

        # สร้างประวัติการเปลี่ยนแปลง (Timeline)
        history_log = IssueStatusHistory(
            issue_id=issue.id,
            status=new_status,
            notes=notes,
            changed_by_id=current_user.id
        )
        db.session.add(history_log)
        db.session.commit()
        flash(f'สถานะของรายงาน #{issue.id} ถูกอัปเดตเป็น "{new_status}" แล้ว', 'success')

    # ไม่ว่าจะสำเร็จหรือพลาด ก็ให้กลับไปที่หน้ารายละเอียดเดิม
    return redirect(url_for('admin.update_issue_page', issue_id=issue.id))

# --- User Management Routes (ส่วนนี้สมบูรณ์ดีแล้ว ไม่ได้แก้ไข) ---
@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('indexuser.html', users=users) # ตรวจสอบชื่อไฟล์ template .html ของคุณ

# ... (โค้ด toggle_admin_status และ delete_user เหมือนเดิม) ...
@admin_bp.route('/user/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin_status(user_id):
    user_to_toggle = User.query.get_or_404(user_id)
    if user_to_toggle.id == current_user.id:
        flash('ไม่สามารถเปลี่ยนสถานะ Admin ของตัวเองได้', 'warning')
        return redirect(url_for('admin.manage_users'))
    if user_to_toggle.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('ไม่สามารถลบสิทธิ์ Admin คนสุดท้ายของระบบได้', 'error')
            return redirect(url_for('admin.manage_users'))
    user_to_toggle.is_admin = not user_to_toggle.is_admin
    db.session.commit()
    status_text = 'เป็น Admin' if user_to_toggle.is_admin else 'เป็นผู้ใช้ทั่วไป'
    flash(f'สถานะของ {user_to_toggle.username} ถูกเปลี่ยนเป็น {status_text} แล้ว', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash('ไม่สามารถลบบัญชีของตัวเองได้', 'warning')
        return redirect(url_for('admin.manage_users'))
    if user_to_delete.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('ไม่สามารถลบ Admin คนสุดท้ายของระบบได้', 'error')
            return redirect(url_for('admin.manage_users'))
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'ผู้ใช้ {user_to_delete.username} ถูกลบเรียบร้อยแล้ว', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'เกิดข้อผิดพลาดในการลบผู้ใช้: {str(e)}', 'error')
    return redirect(url_for('admin.manage_users'))