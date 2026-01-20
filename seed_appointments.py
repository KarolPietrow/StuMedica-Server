from app.database import SessionLocal, engine
from app import models
from datetime import datetime, timedelta
import random

# Upewnij się, że tabele istnieją
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

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
    # Sprawdź czy już nie istnieje (żeby nie dublować przy wielokrotnym uruchomieniu)
    exists = db.query(models.Doctor).filter_by(name=d["name"]).first()
    if not exists:
        new_doc = models.Doctor(name=d["name"], specialization=d["spec"], price_private=d["price"])
        db.add(new_doc)
        created_doctors.append(new_doc)
    else:
        created_doctors.append(exists)

db.commit()

# 2. Generuj wolne terminy na najbliższe 7 dni
for doc in created_doctors:
    for day in range(1, 8):  # Przez następny tydzień
        for hour in [9, 10, 11, 13, 14, 15]:  # Przykładowe godziny
            # Losowo pomijamy niektóre godziny, żeby wyglądało naturalnie
            if random.random() > 0.7: continue

            visit_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=day)

            # Sprawdź duplikat
            exists = db.query(models.Appointment).filter_by(doctor_id=doc.id, date_time=visit_time).first()
            if not exists:
                slot = models.Appointment(
                    doctor_id=doc.id,
                    date_time=visit_time,
                    is_booked=False,
                    type="PRIVATE"
                )
                db.add(slot)

db.commit()
print("Baza danych zasilona lekarzami i terminami!")
db.close()