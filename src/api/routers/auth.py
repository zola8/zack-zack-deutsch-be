import logging
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import JWTError
from jose import jwt
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

AUTH_COOKIE_NAME = "access_token"


@router.get("/status", response_model=dict)
async def auth_status(request: Request):
    """
    Lets the frontend check login state without triggering 401 console noise.
    """
    token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip() or None

    if not token:
        return {"authenticated": False}

    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return {"authenticated": False}

    return {"authenticated": True}


def build_frontend_url(path: str, params: dict | None = None) -> str:
    """
    Builds a safe frontend URL using settings.
    """
    base = settings.FRONTEND_URL.rstrip("/")
    clean_path = path if path.startswith("/") else f"/{path}"
    url = f"{base}{clean_path}"

    if params:
        url = f"{url}?{urlencode(params)}"

    return url


def frontend_redirect(
    path: str,
    params: dict | None = None,
) -> RedirectResponse:
    return RedirectResponse(
        url=build_frontend_url(path, params),
    )


def set_auth_cookie(response: RedirectResponse, token: str) -> None:
    """
    Sets the JWT in a secure, HttpOnly cookie.
    """
    # Browsers REQUIRE secure=True when samesite="none".
    # localhost is exempt and allows Secure cookies over HTTP.
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI

    logger.info(
        "Initiating Google OAuth login. Redirect URI: %s",
        redirect_uri,
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    logger.info("Received Google OAuth callback")

    # 1. Handle Google consent screen errors, e.g. user clicked "Deny"
    google_error = request.query_params.get("error")

    if google_error:
        logger.warning("Google returned error: %s", google_error)

        return frontend_redirect(
            settings.FRONTEND_CALLBACK_PATH,
            {
                "error": google_error,
            },
        )

    # 2. Exchange code for Google access token
    try:
        token = await oauth.google.authorize_access_token(request)
        logger.debug("Successfully obtained access token from Google")
    except Exception as e:
        logger.error(
            "Failed to authorize access token: %s",
            e,
            exc_info=True,
        )

        return frontend_redirect(
            settings.FRONTEND_CALLBACK_PATH,
            {
                "error": "auth_failed",
            },
        )

    # 3. Parse Google ID token / userinfo
    try:
        userinfo = await oauth.google.parse_id_token(token, nonce=None)
    except Exception as e:
        logger.error(
            "Failed to parse ID token: %s",
            e,
            exc_info=True,
        )

        return frontend_redirect(
            settings.FRONTEND_CALLBACK_PATH,
            {
                "error": "no_userinfo",
            },
        )

    if not userinfo:
        logger.error("Failed to parse ID token or userinfo is empty")

        return frontend_redirect(
            settings.FRONTEND_CALLBACK_PATH,
            {
                "error": "no_userinfo",
            },
        )

    logger.info(
        "Successfully parsed userinfo for email: %s",
        userinfo.get("email"),
    )

    # 4. Create or fetch user and generate your app's JWT
    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)

        access_token = await auth_service.authenticate_or_create_user(
            userinfo,
        )

        logger.info("Successfully authenticated/created user. Generating JWT.")
    except Exception as e:
        logger.error(
            "Failed to authenticate/create user: %s",
            e,
            exc_info=True,
        )

        return frontend_redirect(
            settings.FRONTEND_CALLBACK_PATH,
            {
                "error": "user_failed",
            },
        )

    # 5. Redirect to frontend callback and attach the HttpOnly cookie
    response = frontend_redirect(
        settings.FRONTEND_CALLBACK_PATH,
        {
            "status": "success",
        },
    )

    set_auth_cookie(response, access_token)

    return response


@router.get("/logout")
async def logout():
    response = frontend_redirect("/login")

    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
    )

    return response


@router.get("/me", response_model=dict)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    logger.info("Fetching profile for user ID: %s", current_user.id)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
    }
