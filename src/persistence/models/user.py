from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Internal model representing a user in the Turso database."""
    id: int
    email: str
    full_name: Optional[str] = None
    google_id: Optional[str] = None
    picture_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert user object to dictionary for API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "google_id": self.google_id,
            "picture_url": self.picture_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
