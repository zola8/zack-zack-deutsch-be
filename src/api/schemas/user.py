from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


class UserBase(BaseModel):
    """Base schema mirroring the DBUser model fields."""
    id: Optional[int] = None
    email: EmailStr
    google_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr
    google_id: str
    name: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user data. Only mutable fields are included."""
    name: Optional[str] = None


class UserResponse(UserBase):
    """Schema for API responses. All fields are present."""
    id: int
    email: EmailStr
    google_id: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime
