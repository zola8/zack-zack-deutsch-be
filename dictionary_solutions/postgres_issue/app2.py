import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import logging

logger = logging.getLogger(__name__)


import uvicorn
from core.config import settings
from core.database import init_models
from persistence.models.dbuser import DBUser  # noqa: F401
from app import create_app


async def main():
    print("Initializing database models...")
    await init_models()
    print("Database tables created successfully!")


app = create_app()

if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
