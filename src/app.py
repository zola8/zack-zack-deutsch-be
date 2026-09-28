import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# ==========================================
# VERCEL PATH FIX: Ensure both 'src/' and project root are in sys.path
# ==========================================
current_dir = Path(__file__).parent.resolve()  # This is the 'src' directory
project_root = current_dir.parent.resolve()  # This is the project root

print("Current Directory:", current_dir)
print("Project Root:", project_root)

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from api.routers import auth
from api.routers import translate
from core.config import print_settings
from core.config import settings
from core.database import Base
from core.database import engine
from core.logging_config import configure_logging
from services.auth.auth_service import configure_oauth

# ==========================================
# Logging
# ==========================================

configure_logging()
logger = logging.getLogger(__name__)
print_settings()


# ==========================================
# Application setup
# ==========================================

def initialize_database() -> None:
    """Create all database tables."""
    logger.info("Syncing database tables with PostgreSQL...")
    Base.metadata.create_all(bind=engine)


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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=settings.PROJECT_NAME)

    configure_middleware(app)
    configure_oauth()
    register_routers(app)

    return app


# ==========================================
# 2. MODULE-LEVEL EXECUTION (Required for Vercel)
# ==========================================

# Initialize DB (conditionally)
initialize_database()

# Vercel looks for this exact variable name: "app"
app = create_app()

# ==========================================
# 3. LOCAL DEVELOPMENT ONLY
# ==========================================
if __name__ == '__main__':
    logger.info("Starting local development server...")
    print(f"http://localhost:{settings.PORT}/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
