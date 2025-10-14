from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.issue import Issue

# สร้าง Blueprint ชื่อ 'indexuser'
indexuser_bp = Blueprint('indexuser', __name__, template_folder='../templates')

# กำหนดเส้นทางสำหรับหน้าหลักของผู้ใช้
@indexuser_bp.route('/')
@login_required # บังคับให้ต้องล็อกอินก่อนเข้าหน้านี้
def indexuser():
    """
    แสดงหน้าหลักสำหรับผู้ใช้งาน (indexuserissue.html)
    พร้อมดึงข้อมูลสรุปสถิติส่วนตัวจากฐานข้อมูล
    """

    # --- ดึงข้อมูลจากฐานข้อมูล (เฉพาะของผู้ใช้ที่กำลังล็อกอิน) ---

    # 1. นับจำนวนปัญหา "รอดำเนินการ" ของผู้ใช้คนนี้
    pending_count = Issue.query.filter_by(
        user_id=current_user.id, 
        status='รอดำเนินการ'
    ).count()

    # 2. นับจำนวนปัญหา "กำลังดำเนินการ" ของผู้ใช้คนนี้
    in_progress_count = Issue.query.filter_by(
        user_id=current_user.id, 
        status='กำลังดำเนินการ'
    ).count()

    # 3. นับจำนวนปัญหา "แก้ไขแล้ว" ของผู้ใช้คนนี้
    resolved_count = Issue.query.filter_by(
        user_id=current_user.id, 
        status='แก้ไขแล้ว'
    ).count()
    
    # 4. (เพิ่มเติม) ดึงรายการปัญหาล่าสุด 5 รายการของผู้ใช้
    recent_user_issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc()).limit(5).all()

    # --- ส่งข้อมูลทั้งหมดไปให้ Template ---
    # **** FIX: เปลี่ยนชื่อไฟล์ให้เป็น 'indexuserissue.html' ****
    return render_template(
        'indexuserissue.html', 
        pending_issues=pending_count,
        in_progress_issues=in_progress_count,
        resolved_issues=resolved_count,
        recent_issues=recent_user_issues
    )