from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def initialize_models():
    """
    เรียกฟังก์ชันนี้หลังจาก db.init_app(app) และภายใน app.app_context()
    เพื่อ import โมดูลโมเดลอย่างปลอดภัย (หลีกเลี่ยง circular import และ ModuleNotFoundError)
    """
    # ปรับชื่อให้ตรงกับไฟล์จริงในโฟลเดอร์ models/
    try:
        from . import user
    except Exception:
        pass
    try:
        from . import issue
    except Exception:
        pass
    # รองรับทั้งชื่อตัวอย่าง camelCase และ snake_case
    try:
        from . import issueStatusHistory
    except Exception:
        try:
            from . import issue_status_history
        except Exception:
            pass
