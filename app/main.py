from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app import models
from app.database import engine
from app.routers import auth, base, medications, appointments, chat

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="StuMedica API", version="0.6")

origins = [
    "http://stumedica.pl",
    "https://stumedica.pl",
    "http://www.stumedica.pl",
    "https://www.stumedica.pl",
]

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(base.router)
app.include_router(auth.router)
app.include_router(medications.router)
app.include_router(appointments.router)
app.include_router(chat.router)

# uvicorn app.main:app --reload --port 4000
# 🦆