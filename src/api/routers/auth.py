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

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    # authorize_redirect handles the redirection to Google
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=auth_failed")

    userinfo = await oauth.google.parse_id_token(token, nonce=None)
    if not userinfo:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=no_userinfo")

    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    access_token = await auth_service.authenticate_or_create_user(userinfo)

    # Redirect to frontend with token
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login/callback?token={access_token}")


@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }
