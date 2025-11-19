from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from database import UserDatabase
from pydantic import BaseModel

import auth

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

class LoginData(BaseModel):
    email: str
    password: str

@app.post("/login")
async def login(data: LoginData):
    user = db.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Niepoprawny email lub hasło")
    if not auth.verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Niepoprawny email lub hasło")
    return {"success": True, "message": f"Użytkownik {data.email} zalogowany poprawnie"}


# uvicorn main:app --reload --port 4000
