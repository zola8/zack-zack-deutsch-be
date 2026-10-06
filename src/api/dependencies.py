import logging

import turso_serverless
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.user import UserResponse
from core.config import settings
from core.database import get_async_db
from persistence.repositories.dictionary_repository import DictionaryRepository
from persistence.repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.dictionary_service import DictionaryService
from services.grammar_checker_service import GrammarChecker
from services.translator.translator_service import TranslatorService
from services.user_service import UserService

logger = logging.getLogger(__name__)

AUTH_COOKIE_NAME = "access_token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# ==========================================
# GLOBAL TURSO CONNECTIONS
# ==========================================

logger.info("Initializing global Turso connections...")

_turso_dictionary_client = turso_serverless.connect(
    settings.TURSO_DICTIONARY_URL,
    auth_token=settings.TURSO_DICTIONARY_API_KEY,
)


def close_turso_connections():
    """Explicitly close global Turso database connections."""
    logger.info("Closing Turso database connections...")
    try:
        _turso_dictionary_client.close()
        logger.info("Turso connections closed successfully.")
    except Exception as e:
        logger.error("Error closing Turso connections: %s", e)


# ==========================================
# OTHER SERVICES
# ==========================================
def get_translator_service() -> TranslatorService:
    return TranslatorService()


grammar_checker = GrammarChecker("de-DE")


def get_grammar_checker() -> GrammarChecker:
    return grammar_checker


def get_dictionary_repo() -> DictionaryRepository:
    return DictionaryRepository(_turso_dictionary_client)


def get_dictionary_service(repo: DictionaryRepository = Depends(get_dictionary_repo)) -> DictionaryService:
    return DictionaryService(repo)


def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(UserRepository(db))


def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)


# ==========================================
# USER DEPENDENCIES
# ==========================================
async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    token_from_header: str | None = Depends(oauth2_scheme),
) -> UserResponse:
    # 1. Try to get token from the Authorization header first
    token = token_from_header

    # 2. If no header token, try to get it from the HttpOnly cookie
    if not token:
        token = request.cookies.get(AUTH_COOKIE_NAME)

    # 3. If neither exists, reject
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # 4. Decode and validate token
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
