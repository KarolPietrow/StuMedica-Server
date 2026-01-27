# StuMedica Server

Projekt backendu dla aplikacji medycznej wykorzystujący FastAPI, SQLite oraz Gemini API z RAG i Function Calling.

## Wymagania
* Python (testowane na 3.14)
* Klucz API Google Gemini
* (zalecane) Domena do udostępnienia serwera

## Konfiguracja
### Utwórz .env na podstawie .env.template:
* GOOGLE_API_KEY - klucz do GEMINI API
* SECRET_KEY - klucz do tokenów JWT

### Zainstaluj wymagania:
```bash
pip install -r requirements.txt
```

### Skonfiguruj domenę:
* W main.py należy ustawić allow_origins w zależności od domeny, na jakiej będzie działał serwer.
* Jeżeli nie używamy domeny tylko localhosta, to w auth.py w ustawieniach response.set_cookie trzeba wyłączyć zabezpieczenia ciasteczek (secure i samesite).

## Uruchamianie
```bash
uvicorn app.main:app --reload --port 4000
```

## Interfejs
- Dostępne endpointy: https://api.stumedica.pl/docs
- Większość endpointów (w tym /chat/api/) wymaga tokena do autoryzacji - aby użytkownik mógł sprawdzić swoje leki, dodawać nowe, itp.
- Token jest generowany przy logowaniu (/auth/login).
- Najłatwiejsze jest skorzystanie z interfejsu graficznego, czyli aplikacji webowej StuMedica dostępnej pod https://stumedica.pl.
- Aplikacja łączy się z backendem pod https://api.stumedica.pl/.
- Repozytorium z aplikacją webową/mobilną (frontend): https://github.com/PatrycjaSiczek/StuMedica-App