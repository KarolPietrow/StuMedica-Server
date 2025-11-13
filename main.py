from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import UserDatabase

app = FastAPI(title="StuMedica Server")
db = UserDatabase()
# db.create_user("Jan Nowak", "email@example.pl", "haslo123", 151, "patient")

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

# uvicorn main:app --reload --port 4000