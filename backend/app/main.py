from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.session import engine, SessionLocal
from .db.base import Base

# Ensure models are imported so SQLAlchemy can create tables.
from . import models  # noqa: F401
from .api.routes import auth, jobs, applications, chat
from .models.user import User
from .core.security import get_password_hash
from .core.config import settings

app = FastAPI(title="Recruitment System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # ✅ DB is guaranteed to be ready here
    Base.metadata.create_all(bind=engine)
    seed_admin_user()

app.include_router(auth)
app.include_router(jobs)
app.include_router(applications)
app.include_router(chat)

def seed_admin_user():
    if not settings.SEED_ADMIN_EMAIL or not settings.SEED_ADMIN_PASSWORD:
        return
    db = SessionLocal()
    exists = db.query(User).filter(User.email == settings.SEED_ADMIN_EMAIL).first()
    if not exists:
        admin = User(
            email=settings.SEED_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.SEED_ADMIN_PASSWORD),
            role="manager",
        )
        db.add(admin)
        db.commit()
    db.close()

@app.get("/health")
def health():
    return {"ok": True}
