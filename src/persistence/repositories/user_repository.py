import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.user import UserCreate
from api.schemas.user import UserUpdate
from persistence.models.dbuser import DBUser

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing user data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> DBUser | None:
        logger.debug("Fetching user by ID: %d", user_id)
        result = await self.db.execute(select(DBUser).filter(DBUser.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> DBUser | None:
        logger.debug("Fetching user by email: %s", email)
        result = await self.db.execute(select(DBUser).filter(DBUser.email == email))
        return result.scalars().first()

    async def get_user_by_google_id(self, google_id: str) -> DBUser | None:
        logger.debug("Fetching user by Google ID: %s", google_id)
        result = await self.db.execute(select(DBUser).filter(DBUser.google_id == google_id))
        return result.scalars().first()

    async def create_user(self, user_in: UserCreate) -> DBUser:
        logger.info("Creating new user: email=%s", user_in.email)
        db_user = DBUser(
            email=user_in.email,
            name=user_in.name,
            google_id=user_in.google_id,
        )
        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def update_user(self, user_id: int, update_data: UserUpdate) -> DBUser | None:
        logger.info("Updating user ID: %d", user_id)
        result = await self.db.execute(select(DBUser).filter(DBUser.id == user_id))
        user = result.scalars().first()
        if not user:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.flush()
        return user

    async def delete_user(self, user_id: int) -> bool:
        logger.info("Deleting user ID: %d", user_id)
        result = await self.db.execute(select(DBUser).filter(DBUser.id == user_id))
        user = result.scalars().first()
        if not user:
            return False
        await self.db.delete(user)
        await self.db.flush()
        return True

    async def get_all_users(self, limit: int = 100, offset: int = 0) -> list[DBUser]:
        result = await self.db.execute(select(DBUser).offset(offset).limit(limit))
        return result.scalars().all()
