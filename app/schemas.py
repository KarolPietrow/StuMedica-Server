from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
import re

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str
    # age: int
    account_type: str

class UserLogin(UserBase):
    password: str


class MedicationBase(BaseModel):
    name: str
    dosage: str
    note: Optional[str] = None
    reminders: List[str] = []

    @field_validator('reminders')
    def validate_time_format(cls, v):
        time_regex = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
        for time_str in v:
            if not time_regex.match(time_str):
                raise ValueError(f"Nieprawidłowy format godziny: {time_str}. Wymagany HH:MM")
        return v

class MedicationCreate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: int
    user_id: int
    is_active: bool

    class Config:
        from_attributes = True