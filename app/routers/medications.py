from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)

@router.get("/", response_model=List[schemas.MedicationResponse])
def get_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Medication).filter(
        models.Medication.user_id == current_user.id,
        models.Medication.is_active == True
    ).all()

@router.post("/", response_model=schemas.MedicationResponse)
def create_medication(
    medication: schemas.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_med = models.Medication(
        **medication.model_dump(),
        user_id=current_user.id
    )
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med


@router.delete("/{med_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
        med_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    med_query = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.user_id == current_user.id
    )

    med = med_query.first()
    if not med:
        raise HTTPException(status_code=404, detail="Lek nie znaleziony")

    med_query.delete(synchronize_session=False)
    db.commit()
    return None