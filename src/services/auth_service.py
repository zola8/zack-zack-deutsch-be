from authlib.integrations.starlette_client import OAuth

from api.schemas.user import UserCreate
from core.config import settings
from core.security import create_access_token
from repositories.user_repository import UserRepository

# Initialize OAuth instance
oauth = OAuth()

# Register Google Client
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    client_kwargs={'scope': 'openid email profile'}
)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_or_create_user(self, user_info: dict):
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Check if user exists by Google ID or Email
        db_user = self.user_repo.get_user_by_google_id(google_id)
        if not db_user:
            db_user = self.user_repo.get_user_by_email(email)

        if not db_user:
            # Create new user
            user_in = UserCreate(
                email=email, full_name=name,
                google_id=google_id, picture_url=picture
            )
            db_user = self.user_repo.create_user(user_in)

        # Generate JWT
        return create_access_token(data={"sub": str(db_user.id)})
