from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserResponse(UserBase):
    id: int
    google_id: str
    created_at: datetime

    class Config:
        from_attributes = True
