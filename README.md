# StuMedica Server

Projekt backendu dla aplikacji medycznej wykorzystujący FastAPI, SQLite oraz Gemini API z RAG i Function Calling.

## Wymagania
* Python (testowane na 3.14)
* Klucz API Google Gemini
* (zalecane) Domena do udostępnienia serwera

## Konfiguracja
Utwórz .env na podstawie .env.template:
* GOOGLE_API_KEY - 
Uruchom w terminalu:
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 4000
```