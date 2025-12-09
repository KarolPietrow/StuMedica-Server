from http.client import HTTPResponse
from urllib.error import HTTPError

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from database import UserDatabase

import auth
from schemas import UserLogin, UserCreate

# import database

app = FastAPI(title="StuMedica Server")
db = UserDatabase()
# db.create_user("Andrzej Nowak", "email3@example.pl", "haslo123", 151, "patient")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def login(data: UserLogin):
    user = db.get_user_by_email(data.email)

    if not user or not auth.verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Niepoprawne dane.")

    return {"success": True, "message": f"Zalogowano", "token": "TODO"}

@app.post("/register")
async def register(data: UserCreate):
    if db.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email zajęty")

    password_hash = auth.get_password_hash(data.password)

    success, result = db.create_user(
        name=data.name,
        email=data.email,
        password_hash=password_hash,
        account_type=data.account_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=result)

    return {"success": True, "message": "Utworzono konto"}


# uvicorn main:app --reload --port 4000
