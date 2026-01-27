# StuMedica Server

Projekt backendu dla aplikacji medycznej wykorzystujący FastAPI, SQLite oraz Gemini API z RAG i Function Calling.

## Wymagania
* Python 3.9+
* Klucz API Google Gemini (zmienna `GOOGLE_API_KEY`)

## 1. Instalacja zależności
Uruchom w terminalu:
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 4000
```