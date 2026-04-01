"""
Run this script to create an admin user or promote an existing user to admin.
Usage: python create_admin.py
"""
from database.db import SessionLocal
from models.user import User, UserRole
from utils.auth import hash_password

db = SessionLocal()

email = input("Enter admin email: ").strip()
existing = db.query(User).filter(User.email == email).first()

if existing:
    existing.role = UserRole.admin
    db.commit()
    print(f"✅ '{email}' has been promoted to admin.")
else:
    name = input("Enter name: ").strip()
    password = input("Enter password: ").strip()
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.admin
    )
    db.add(user)
    db.commit()
    print(f"✅ Admin user '{email}' created successfully.")

db.close()
