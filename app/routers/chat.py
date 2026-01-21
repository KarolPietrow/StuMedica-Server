import os
from datetime import datetime
from typing import List

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

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]

@router.post("/ask")
def ask_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    def get_my_medications():
        """Pobiera listę leków aktualnie przyjmowanych przez pacjenta."""
        meds = db.query(models.Medication).filter(
            models.Medication.user_id == current_user.id,
            models.Medication.is_active == True
        ).all()

        if not meds:
            return "Pacjent nie ma żadnych zapisanych leków."

        return ", ".join([f"{m.name} ({m.dosage})" for m in meds])

    def add_medication(nazwa_leku: str, dawka: str):
        """Dodaje nowy lek do listy pacjenta.

        Args:
            nazwa_leku: Nazwa leku np. Ibuprofen.
            dawka: Opis dawkowania np. 200mg rano.
        """
        new_med = models.Medication(
            name=nazwa_leku,
            dosage=dawka,
            user_id=current_user.id,
            is_active=True
        )
        db.add(new_med)
        db.commit()
        return f"Pomyślnie dodano lek: {nazwa_leku}, dawka: {dawka}."

    def find_available_slots(specjalizacja: str = None):
        """Wyszukuje wolne terminy wizyt.
        Args:
            specjalizacja: (Opcjonalnie) Specjalizacja lekarza np. 'Kardiolog', 'Internista'.
                           Jeśli puste, zwraca wszystkie wolne terminy.
        """
        query = db.query(models.Appointment).join(models.Doctor).filter(
            models.Appointment.is_booked == False,
            models.Appointment.date_time > datetime.now()
        )

        if specjalizacja:
            query = query.filter(models.Doctor.specialization.ilike(f"%{specjalizacja}%"))

        slots = query.order_by(models.Appointment.date_time).limit(10).all()

        if not slots:
            return "Nie znaleziono wolnych terminów dla podanych kryteriów."

        result = "Dostępne terminy:\n"
        for slot in slots:
            dt_str = slot.date_time.strftime("%Y-%m-%d %H:%M")
            result += f"- ID: {slot.id} | Lekarz: {slot.doctor.name} ({slot.doctor.specialization}) | Data: {dt_str} | Cena: {slot.doctor.price_private} PLN\n"

        return result

    def book_appointment_by_id(wizyta_id: int, powod: str = "Konsultacja"):
        """Rezerwuje wizytę na podstawie jej numeru ID (który znalazłeś wcześniej).
        Args:
            wizyta_id: Numer ID wolnego terminu (liczba).
            powod: Krótki powód wizyty podany przez pacjenta.
        """
        appointment = db.query(models.Appointment).filter(
            models.Appointment.id == wizyta_id,
            models.Appointment.is_booked == False
        ).first()

        if not appointment:
            return "Błąd: Ten termin jest niedostępny lub podano błędne ID."

        appointment.is_booked = True
        appointment.patient_id = current_user.id
        appointment.notes = powod

        db.commit()

        doctor_name = appointment.doctor.name
        date_str = appointment.date_time.strftime("%Y-%m-%d %H:%M")
        return f"Sukces! Zarezerwowano wizytę u {doctor_name} na dzień {date_str}."

    def get_my_appointments_history():
        """Pobiera historię i nadchodzące wizyty pacjenta."""
        apps = db.query(models.Appointment).join(models.Doctor).filter(
            models.Appointment.patient_id == current_user.id
        ).order_by(models.Appointment.date_time.desc()).all()

        if not apps:
            return "Nie masz żadnych zarezerwowanych wizyt."

        result = "Twoje wizyty:\n"
        for app in apps:
            dt_str = app.date_time.strftime("%Y-%m-%d %H:%M")
            status = "Zarezerwowana" if app.date_time > datetime.now() else "Archiwalna"
            result += f"- {dt_str} | {app.doctor.name} ({app.doctor.specialization}) | Status: {status}\n"

        return result

    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        if not request.history:
            return {"response": "Pusta wiadomość"}

        last_message = request.history[-1].content

        previous_messages = []
        for msg in request.history[:-1]:
            previous_messages.append(
                types.Content(
                    role=msg.role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        chat = client.chats.create(
            model="gemini-2.0-flash",
            history=previous_messages,
            config=types.GenerateContentConfig(
                tools=[
                    get_my_medications,
                    add_medication,
                    find_available_slots,
                    book_appointment_by_id,
                    get_my_appointments_history
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
                system_instruction=(
                    "Jesteś inteligentnym asystentem medycznym w aplikacji StuMedica. Nazywasz się StuMedicAI."
                    "Twoje zadania:\n"
                    "1. Zarządzanie lekami pacjenta (wyświetlanie, dodawanie).\n"
                    "2. Umawianie wizyt lekarskich.\n"
                    "ZASADY UMAWIANIA WIZYT:\n"
                    "- Najpierw ZAWSZE szukaj dostępnych terminów używając `find_available_slots`.\n"
                    "- Po znalezieniu listy, zapytaj użytkownika, który termin wybiera.\n"
                    "- Gdy użytkownik wybierze termin, użyj `book_appointment_by_id` przekazując odpowiednie ID znalezione w poprzednim kroku.\n"
                    "- Nie zmyślaj terminów, korzystaj tylko z tego, co zwróci funkcja.\n"
                )
            )
        )

        response = chat.send_message(last_message)

        if response.text:
            return {"response": response.text}
        else:
            return {"response": "Nie mogę odpowiedzieć na to pytanie (blokada bezpieczeństwa lub błąd generowania)."}

    except Exception as e:
        print(f"Błąd Google GenAI: {e}")
        return {"response": f"Przepraszam, wystąpił błąd systemu AI: {str(e)}"}