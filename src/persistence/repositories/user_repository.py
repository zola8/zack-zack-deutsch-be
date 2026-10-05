from api.schemas.user import UserCreate
from persistence.models.user import User


class UserRepository:
    def __init__(self, conn):
        """Initialize with an active turso_serverless connection object."""
        self.conn = conn

    def get_user_by_id(self, user_id: int) -> User | None:
        cursor = self.conn.execute(
            "SELECT id, email, full_name, google_id, picture_url, created_at, updated_at FROM users WHERE id = ?",
            [user_id]
        )
        row = cursor.fetchone()
        return self._row_to_user(row)

    def get_user_by_email(self, email: str):
        cursor = self.conn.execute(
            "SELECT id, email, full_name, google_id, picture_url, created_at, updated_at FROM users WHERE email = ?",
            [email]
        )
        row = cursor.fetchone()
        return self._row_to_user(row)

    def get_user_by_google_id(self, google_id: str):
        cursor = self.conn.execute(
            "SELECT id, email, full_name, google_id, picture_url, created_at, updated_at FROM users WHERE google_id = ?",
            [google_id]
        )
        row = cursor.fetchone()
        return self._row_to_user(row)

    def create_user(self, user_in: UserCreate):
        cursor = self.conn.execute("""
            INSERT INTO users (email, full_name, google_id, picture_url)
            VALUES (?, ?, ?, ?)
            RETURNING id, email, full_name, google_id, picture_url, created_at, updated_at
        """, [user_in.email, user_in.full_name, user_in.google_id, user_in.picture_url])

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
            full_name=row[2],
            google_id=row[3],
            picture_url=row[4],
            created_at=row[5],
            updated_at=row[6]
        )
