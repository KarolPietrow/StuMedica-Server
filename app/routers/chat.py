import os
from google import genai
from google.genai import types
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv

from app.database import get_db
from app.dependencies import get_current_user
from app import models

load_dotenv()
router = APIRouter(
    prefix="/chat",
    tags=["AI Assistant"]
)

class ChatRequest(BaseModel):
    message: str

@router.post("/ask")
def ask_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # --- 1. DEFINICJE NARZĘDZI (Wewnątrz funkcji, by mieć dostęp do `db` i `user`) ---

    # Funkcja do pobierania leków
    def get_my_medications():
        """Pobiera listę leków aktualnie przyjmowanych przez pacjenta."""
        meds = db.query(models.Medication).filter(
            models.Medication.user_id == current_user.id,
            models.Medication.is_active == True
        ).all()

        if not meds:
            return "Pacjent nie ma żadnych zapisanych leków."

        return ", ".join([f"{m.name} ({m.dosage})" for m in meds])

    # Funkcja do dodawania leku
    def add_medication(nazwa_leku: str, dawka: str):
        """Dodaje nowy lek do listy pacjenta.

        Args:
            nazwa_leku: Nazwa leku np. Ibuprofen, Witamina C.
            dawka: Opis dawkowania np. 200mg rano, 1 tabletka dziennie.
        """
        # Tu można dodać walidację (Guardrails), np. czy dawka nie jest zbyt duża
        new_med = models.Medication(
            name=nazwa_leku,
            dosage=dawka,
            user_id=current_user.id,
            is_active=True
        )
        db.add(new_med)
        db.commit()
        return f"Pomyślnie dodano lek: {nazwa_leku}, dawka: {dawka}."

    # --- 2. KONFIGURACJA MODELU Z NARZĘDZIAMI ---

    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[get_my_medications, add_medication],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                system_instruction="Jesteś pomocnym asystentem medycznym w aplikacji StuMedica. "
                                   "Masz dostęp do leków pacjenta i możesz zarządzać jego listą. "
                                   "Odpowiadaj krótko i rzeczowo. Nie udawaj lekarza."
            )
        )

        # --- 3. ROZMOWA ---

        response = chat.send_message(request.message)

        # W nowym SDK odpowiedź tekstowa jest w .text (jeśli nie zablokowano przez safety filters)
        if response.text:
            return {"response": response.text}
        else:
            return {"response": "Nie mogę odpowiedzieć na to pytanie (blokada bezpieczeństwa lub błąd generowania)."}

    except Exception as e:
        print(f"Błąd Google GenAI: {e}")
        return {"response": f"Przepraszam, wystąpił błąd systemu AI: {str(e)}"}