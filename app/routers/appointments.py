from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.get("/doctors", response_model=List[schemas.DoctorResponse])
def get_doctors(
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Doctor)
    if specialization:
        query = query.filter(models.Doctor.specialization == specialization)
    return query.all()


@router.get("/slots", response_model=List[schemas.AppointmentResponse])
def get_available_slots(
        specialization: Optional[str] = None,
        doctor_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Appointment).filter(
        models.Appointment.is_booked == False,
        models.Appointment.date_time > datetime.now()
    )

    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)

    if specialization:
        query = query.join(models.Doctor).filter(models.Doctor.specialization == specialization)

    return query.order_by(models.Appointment.date_time).all()


@router.post("/{appointment_id}/book", response_model=schemas.AppointmentResponse)
def book_appointment(
        appointment_id: int,
        booking_data: schemas.AppointmentCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.is_booked == False
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Termin niedostępny lub nie istnieje")

    appointment.is_booked = True
    appointment.patient_id = current_user.id
    appointment.notes = booking_data.notes

    db.commit()
    db.refresh(appointment)

    # background_tasks.add_task(
    #     send_appointment_confirmation,
    #     to_email=current_user.email,
    #     patient_name=current_user.name,
    #     doctor_name=appointment.doctor.name,
    #     specialization=appointment.doctor.specialization,
    #     date_time=appointment.date_time
    # )

    return appointment

@router.get("/my-history", response_model=List[schemas.AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Appointment).filter(
        models.Appointment.patient_id == current_user.id
    ).order_by(models.Appointment.date_time.desc()).all()