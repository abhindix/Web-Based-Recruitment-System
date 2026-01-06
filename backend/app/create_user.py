from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin():
    db: Session = SessionLocal()

    email = "admin@test.com"
    password = "admin123"

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

if __name__ == "__main__":
    create_admin()
