# ที่ไฟล์: create_admin.py

from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():
    print("--- สร้างบัญชีผู้ดูแลระบบ ---")

    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    
    # **** ย้ายบรรทัดนี้ขึ้นมา ****
    password = input("Enter admin password: ") 
    
    first_name = input("Enter admin first name: ")
    last_name = input("Enter admin last name: ")
    telephone = input("Enter admin telephone: ")

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        print(f"!! มีชื่อผู้ใช้ '{username}' หรืออีเมล '{email}' อยู่ในระบบแล้ว กรุณาลองใหม่")
    else:
        new_admin = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            first_name=first_name,
            last_name=last_name,
            telephone=telephone,
            is_admin=True
        )

        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ สร้างบัญชี Admin '{username}' เรียบร้อยแล้ว!")