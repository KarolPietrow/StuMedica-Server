from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session

from app import security, models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import UserLogin, UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not security.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Niepoprawne dane logowania.")

    access_token = security.create_access_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # True na produkcji (wymaga HTTPS), False na localhost
        samesite="lax",  # Zabezpieczenie CSRF
        max_age=24 * 3600
    )

    return {
        "success": True,
        "message": "Zalogowano",
        "token": access_token,
        "user": user.name
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True, "message": "Wylogowano"}

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    clean_name = " ".join(data.name.split())
    clean_email = data.email.strip().replace(" ", "")

    existing_user = db.query(models.User).filter(models.User.email == clean_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email zajęty")

    password_hash = security.get_password_hash(data.password)

    new_user = models.User(
        name=clean_name,
        email=clean_email,
        password_hash=password_hash,
        account_type=data.account_type
        # is_active=True (domyślnie w modelu)
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Błąd podczas tworzenia konta")

    return {"success": True, "message": "Utworzono konto"}

@router.get("/me")
async def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "success": True,
        "name": current_user.name,
        "email": current_user.email,
        "account_type": current_user.account_type
    }