import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin():
    email = os.environ.get("SEED_ADMIN_EMAIL", "")
    password = os.environ.get("SEED_ADMIN_PASSWORD", "")

    if not email or not password:
        print("Set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD environment variables first.")
        return

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print("User already exists")
            return

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.MANAGER.value,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        print("Admin user created")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
