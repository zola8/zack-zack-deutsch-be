import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routers import auth
from api.routers import translate
from core.config import log_settings
from core.config import settings
from core.database import Base
from core.database import engine
from core.logging_config import configure_logging
from services.auth_service import configure_oauth

logger = logging.getLogger(__name__)

configure_logging()


def configure_middleware(app: FastAPI) -> None:
    """Add all middleware to the FastAPI application."""
    # Session middleware for OAuth state management
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # CORS middleware for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI) -> None:
    """Register all API routers with the application."""
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(translate.router, prefix=settings.API_V1_STR)


def initialize_database() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=settings.PROJECT_NAME)

    configure_middleware(app)
    configure_oauth()
    register_routers(app)

    @app.get("/")
    async def root():
        return {"message": "Welcome to Zack Zack Deutsch Backend"}

    return app


def main() -> None:
    """Run the application with uvicorn."""
    log_settings()
    initialize_database()
    app = create_app()

    print(f"http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == '__main__':
    main()
