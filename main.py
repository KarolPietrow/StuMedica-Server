from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from database import UserDatabase

import auth
from dependencies import get_current_user
from schemas import UserLogin, UserCreate

app = FastAPI(title="StuMedica Server")
db = UserDatabase()
# db.create_user("Andrzej Nowak", "email3@example.pl", "haslo123", 151, "patient")

origins = [
    "http://localhost:8081",
    "http://localhost:8082",

    # "http://stumedica.pl",
    "https://stumedica.pl",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def main_site_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <title>StuMedica API</title>
    </head>
    <body>
    
    <h1>Witamy w StuMedica API! 💖</h1>
    
    </body>
    </html>
    """

@app.get("/hello")
async def get_test_value():
    return {"success": True, "message": "Welcome to the StuMedica API!"}

@app.post("/login")
def login(data: UserLogin, response: Response):
    user = db.get_user_by_email(data.email)

    if not user or not auth.verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Niepoprawne dane logowania.")

    access_token = auth.create_access_token(data={"sub": user['email']})

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
        "user": user["name"]
    }

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True, "message": "Wylogowano"}

@app.post("/register")
def register(data: UserCreate):
    clean_name = " ".join(data.name.split())
    clean_email = data.email.strip().replace(" ", "")

    password_hash = auth.get_password_hash(data.password)

    if db.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email zajęty")

    success, result = db.create_user(
        name=clean_name,
        email=clean_email,
        password_hash=password_hash,
        account_type=data.account_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=result)

    return {"success": True, "message": "Utworzono konto"}

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "name": current_user["name"],
        "email": current_user["email"]
    }


# uvicorn main:app --reload --port 4000
# 🦆

