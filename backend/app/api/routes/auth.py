from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ...core.security import create_access_token, verify_password
from ...crud import user as user_crud
from ...models.user import User, UserRole
from ...schemas.auth import RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role_value = payload.role.value if isinstance(payload.role, UserRole) else str(payload.role)
    if role_value not in {UserRole.MANAGER.value, UserRole.APPLICANT.value}:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = user_crud.create_user(
        db=db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=role_value,
    )

    # Auto-login after registration
    token = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses `username` for the email
    user = user_crud.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_str = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token_str, "token_type": "bearer", "role": user.role}


@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return {"id": current.id, "email": current.email, "full_name": current.full_name, "role": current.role}
