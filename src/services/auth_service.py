from datetime import datetime
from datetime import timedelta
from datetime import timezone

from authlib.integrations.starlette_client import OAuth
from jose import jwt

from api.schemas.user import UserCreate
from core.config import settings
from persistence.repositories.user_repository import UserRepository

oauth = OAuth()


def configure_oauth():
    """Register OAuth clients."""
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        client_kwargs={'scope': 'openid email profile'}
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=settings.ALGORITHM)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_or_create_user(self, user_info: dict):
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        db_user = self.user_repo.get_user_by_google_id(google_id)
        if not db_user:
            db_user = self.user_repo.get_user_by_email(email)

        if not db_user:
            user_in = UserCreate(
                email=email, full_name=name,
                google_id=google_id, picture_url=picture
            )
            db_user = self.user_repo.create_user(user_in)

        return create_access_token(data={"sub": str(db_user.id)})
