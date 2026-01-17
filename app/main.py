from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import models
from app.database import engine
from app.routers import auth, base, medications


models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="StuMedica API", version="0.5")

origins = [
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:3000",
    "https://stumedica.pl",
    "https://www.stumedica.pl",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(base.router)
app.include_router(auth.router)
app.include_router(medications.router)

# uvicorn app.main:app --reload --port 4000
# 🦆