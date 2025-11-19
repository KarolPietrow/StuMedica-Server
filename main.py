from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/api/value")
async def value():
    return {"success": True, "message": "Hello World"}

class LoginData(BaseModel):
    email: str
    password: str

@app.post("/api/login")
async def login(data: LoginData):
    user = db.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Niepoprawny email lub hasło")
    if not auth.verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Niepoprawny email lub hasło")
    return {"success": True, "message": f"Użytkownik {data.email} zalogowany poprawnie"}


# uvicorn main:app --reload --port 4000
