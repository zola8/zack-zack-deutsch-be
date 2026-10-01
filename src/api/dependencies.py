from pathlib import Path

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from persistence.repositories.dictionary_repository import DictionaryRepository
from persistence.repositories.user_repository import UserRepository
from services.grammar_checker.grammar_checker import GrammarChecker
from services.translator.translator_service import TranslatorService

AUTH_COOKIE_NAME = "access_token"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

SRC_DIR = Path(__file__).parent.parent

DICTIONARY_DB_PATH = SRC_DIR / "data" / "dictionary.db"


async def get_current_user(
    request: Request,
    token_from_header: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
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

    # 4
    payload = jwt.decode(
        token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(sub)
    except (TypeError, ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 5. Fetch user from DB by ID
    user = UserRepository(db).get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_translator_service() -> TranslatorService:
    """Dependency provider for TranslatorService."""
    return TranslatorService()


_grammar_checker = GrammarChecker("de-DE")


def get_grammar_checker() -> GrammarChecker:
    """Dependency provider for GrammarCheckerService."""
    return _grammar_checker


def get_dictionary_repo() -> DictionaryRepository:
    return DictionaryRepository(str(DICTIONARY_DB_PATH))
