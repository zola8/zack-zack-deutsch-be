from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    google_id: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
