from api.schemas.user import UserCreate
from persistence.models.user import User


class UserRepository:
    def __init__(self, conn):
        """Initialize with an active turso_serverless connection object."""
        self.conn = conn

    def get_user_by_id(self, user_id: int) -> User | None:
        cursor = self.conn.execute(
            "SELECT id, email, google_id, name, given_name, family_name, picture, created_at, updated_at FROM users WHERE id = ?",
            [user_id]
        )
        return self._row_to_user(cursor.fetchone())

    def get_user_by_email(self, email: str) -> User | None:
        cursor = self.conn.execute(
            "SELECT id, email, google_id, name, given_name, family_name, picture, created_at, updated_at FROM users WHERE email = ?",
            [email]
        )
        return self._row_to_user(cursor.fetchone())

    def get_user_by_google_id(self, google_id: str) -> User | None:
        cursor = self.conn.execute(
            "SELECT id, email, google_id, name, given_name, family_name, picture, created_at, updated_at FROM users WHERE google_id = ?",
            [google_id]
        )
        return self._row_to_user(cursor.fetchone())

    def create_user(self, user_in: UserCreate) -> User:
        cursor = self.conn.execute("""
            INSERT INTO users (email, google_id, name, given_name, family_name, picture)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id, email, google_id, name, given_name, family_name, picture, created_at, updated_at
        """, [
            user_in.email,
            user_in.google_id,
            user_in.name,
            user_in.given_name,
            user_in.family_name,
            user_in.picture
        ])
        row = cursor.fetchone()
        self.conn.commit()
        return self._row_to_user(row)

    def _row_to_user(self, row) -> User | None:
        """Convert a Turso row tuple to a User dataclass."""
        if not row:
            return None
        return User(
            id=row[0],
            email=row[1],
            google_id=row[2],
            name=row[3],
            given_name=row[4],
            family_name=row[5],
            picture=row[6],
            created_at=row[7],
            updated_at=row[8]
        )
