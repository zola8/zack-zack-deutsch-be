import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from core.config import settings
from core.database import get_db
from models.user import User
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.auth_service import oauth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    logger.info(f"Initiating Google OAuth login. Redirect URI: {redirect_uri}")

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    logger.info("Received Google OAuth callback")

    try:
        token = await oauth.google.authorize_access_token(request)
        logger.debug("Successfully obtained access token from Google")
    except Exception as e:
        logger.error(f"Failed to authorize access token: {e}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=auth_failed")

    userinfo = await oauth.google.parse_id_token(token, nonce=None)
    if not userinfo:
        logger.error("Failed to parse ID token or userinfo is empty")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=no_userinfo")

    logger.info(f"Successfully parsed userinfo for email: {userinfo.get('email')}")

    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    access_token = await auth_service.authenticate_or_create_user(userinfo)

    logger.info(f"Successfully authenticated/created user. Generating JWT.")

    # Redirect to frontend with token
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login/callback?token={access_token}")


@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    logger.info(f"Fetching profile for user ID: {current_user.id}")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }
