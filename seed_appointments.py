from app.database import SessionLocal, engine
from app import models
from datetime import datetime, timedelta, time
import random

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# USTAWIENIA DATY
YEAR = 2026
START_MONTH = 2
START_DAY = 1
END_MONTH = 3
END_DAY = 31

# 1. Dodaj lekarzy
doctors_data = [
    {"name": "dr n. med. Anna Nowak", "spec": "Kardiolog", "price": 200.0},
    {"name": "lek. Piotr Kowalski", "spec": "Internista", "price": 150.0},
    {"name": "dr Janusz Malinowski", "spec": "Stomatolog", "price": 250.0},
    {"name": "lek. Maria Wiśniewska", "spec": "Dermatolog", "price": 180.0},
    {"name": "dr Adam Zieliński", "spec": "Okulista", "price": 160.0},
]

created_doctors = []
for d in doctors_data:
    exists = db.query(models.Doctor).filter_by(name=d["name"]).first()
    if not exists:
        new_doc = models.Doctor(name=d["name"], specialization=d["spec"], price_private=d["price"])
        db.add(new_doc)
        created_doctors.append(new_doc)
        print(f"Dodano lekarza: {d['name']}")
    else:
        created_doctors.append(exists)
        print(f"Lekarz istnieje: {d['name']}")

db.commit()

start_date = datetime(YEAR, START_MONTH, START_DAY)
end_date = datetime(YEAR, END_MONTH, END_DAY)

# Oblicz liczbę dni w zakresie
delta_days = (end_date - start_date).days

print(f"\n--- Generowanie terminów od {start_date.date()} do {end_date.date()} ---")
count = 0

for i in range(delta_days + 1):
    current_date = start_date + timedelta(days=i)

    # SPRAWDZENIE WEEKENDU
    # weekday(): 0=Pon, 1=Wt, ..., 5=Sob, 6=Niedz
    if current_date.weekday() >= 5:
        continue  # Pomiń soboty i niedziele

    # Dla każdego lekarza
    for doc in created_doctors:
        # Godziny przyjęć (np. od 9:00 do 16:00)
        possible_hours = [9, 10, 11, 12, 13, 14, 15, 16]

        for hour in possible_hours:
            if random.random() > 0.5:
                continue

            visit_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)

            # Sprawdź, czy taki termin już istnieje w bazie (żeby nie dublować)
            exists = db.query(models.Appointment).filter_by(
                doctor_id=doc.id,
                date_time=visit_time
            ).first()

            if not exists:
                slot = models.Appointment(
                    doctor_id=doc.id,
                    date_time=visit_time,
                    is_booked=False,
                    type="PRIVATE"
                )
                db.add(slot)
                count += 1

db.commit()
print(f"\nSukces! Wygenerowano {count} nowych wolnych terminów.")
db.close()