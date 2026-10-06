import logging

from sqlalchemy.orm import Session

from api.schemas.user import UserCreate
from api.schemas.user import UserUpdate
from persistence.models.dbuser import DBUser

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing user data."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> DBUser | None:
        """Fetch a user by their ID."""
        logger.debug("Fetching user by ID: %d", user_id)
        user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if user:
            logger.debug("User found: id=%d, email=%s", user.id, user.email)
        else:
            logger.debug("No user found with ID: %d", user_id)
        return user

    def get_user_by_email(self, email: str) -> DBUser | None:
        """Fetch a user by their email address."""
        logger.debug("Fetching user by email: %s", email)
        user = self.db.query(DBUser).filter(DBUser.email == email).first()
        if user:
            logger.debug("User found: id=%d, email=%s", user.id, user.email)
        else:
            logger.debug("No user found with email: %s", email)
        return user

    def get_user_by_google_id(self, google_id: str) -> DBUser | None:
        """Fetch a user by their Google ID."""
        logger.debug("Fetching user by Google ID: %s", google_id)
        user = self.db.query(DBUser).filter(DBUser.google_id == google_id).first()
        if user:
            logger.debug("User found: id=%d, email=%s", user.id, user.email)
        else:
            logger.debug("No user found with Google ID: %s", google_id)
        return user

    def create_user(self, user_in: UserCreate) -> DBUser:
        """Create a new user in the database."""
        logger.info("Creating new user: email=%s, google_id=%s", user_in.email, user_in.google_id)

        db_user = DBUser(
            email=user_in.email,
            name=user_in.name,
            google_id=user_in.google_id,
        )

        self.db.add(db_user)
        self.db.flush()
        self.db.refresh(db_user)

        logger.info("User staged for creation: id=%d, email=%s", db_user.id, db_user.email)
        return db_user

    def update_user(self, user_id: int, update_data: UserUpdate) -> DBUser | None:
        """Update an existing user's data."""
        logger.info("Updating user ID: %d", user_id)

        user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            logger.warning("Cannot update: user not found with ID: %d", user_id)
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)

        logger.info("User update staged: id=%d, fields=%s", user.id, list(update_dict.keys()))
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by their ID. """
        logger.info("Deleting user ID: %d", user_id)

        user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            logger.warning("Cannot delete: user not found with ID: %d", user_id)
            return False

        self.db.delete(user)
        logger.info("User deletion staged: id=%d", user_id)
        return True

    def get_all_users(self, limit: int = 100, offset: int = 0) -> list[DBUser]:
        """Fetch all users with pagination."""
        logger.debug("Fetching all users: limit=%d, offset=%d", limit, offset)
        users = self.db.query(DBUser).offset(offset).limit(limit).all()
        logger.debug("Found %d users", len(users))
        return users
