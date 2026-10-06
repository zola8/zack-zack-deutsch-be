from datetime import datetime
from datetime import timedelta
from datetime import timezone

from authlib.integrations.starlette_client import OAuth
from jose import jwt

from api.schemas.user import UserCreate
from core.config import settings
from services.user_service import UserService

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
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_or_create_user(self, user_info: dict):
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')

        existing_user = self.user_service.get_user_by_google_id(google_id)
        if not existing_user:
            existing_user = self.user_service.get_user_by_email(email)

        if not existing_user:
            user_in = UserCreate(
                email=email,
                google_id=google_id,
                name=name,
            )
            existing_user = self.user_service.create_user(user_in)

        # Generate JWT with user ID
        return create_access_token(data={"sub": str(existing_user.id)})
