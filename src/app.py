import sys
from pathlib import Path

# ==========================================
# VERCEL PATH FIX
# ==========================================
current_dir = Path(__file__).parent.resolve()  # This is the 'src' directory
project_root = current_dir.parent.resolve()  # This is the project root

print("Current Directory:", current_dir)
print("Project Root:", project_root)

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.dependencies import close_turso_connections
from api.routers import auth
from api.routers import translate
from api.routers import grammar
from api.routers import dictionary
from core.config import print_settings
from core.config import settings
from core.logging_config import configure_logging
from core.database import Base
from core.database import engine
from persistence.models.dbuser import DBUser  # noqa: F401
from services.auth_service import configure_oauth
from api.dependencies import _grammar_checker

# ==========================================
# Logging
# ==========================================

configure_logging()
logger = logging.getLogger(__name__)
print_settings()


# ==========================================
# Application setup
# ==========================================


def configure_middleware(app: FastAPI) -> None:
    """Add all middleware to the FastAPI application."""

    # Session middleware for OAuth state management
    app.add_middleware(SessionMiddleware, secret_key=settings.AUTH_SECRET_KEY)

    # CORS middleware for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.FRONTEND_URL,
            "http://127.0.0.1:5173",
            "https://zack-zack-deutsch-fe.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI) -> None:
    """Register all API routers with the application."""
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(translate.router, prefix=settings.API_V1_STR)
    app.include_router(grammar.router, prefix=settings.API_V1_STR)
    app.include_router(dictionary.router, prefix=settings.API_V1_STR)


def initialize_database() -> None:
    """Create all database tables."""
    logger.info("Syncing database tables with PostgreSQL...")
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete.")

    yield

    logger.info("Shutting down application, closing grammar checker client...")
    close_turso_connections()
    await _grammar_checker.close()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    initialize_database()
    configure_middleware(app)
    configure_oauth()
    register_routers(app)

    return app


# ==========================================
# 2. MODULE-LEVEL EXECUTION (Required for Vercel)
# ==========================================

# Vercel looks for this exact variable name: "app"
app = create_app()

# ==========================================
# 3. LOCAL DEVELOPMENT ONLY
# ==========================================
if __name__ == '__main__':
    logger.info("Starting local development server...")
    print(f"http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
