from sqlalchemy.orm import Session

from api.schemas.user import UserCreate
from models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_google_id(self, google_id: str):
        return self.db.query(User).filter(User.google_id == google_id).first()

    def create_user(self, user_in: UserCreate):
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            google_id=user_in.google_id,
            picture_url=user_in.picture_url
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
