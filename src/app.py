import logging

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI

from core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/")
async def homepage():
    return {
        "version": "0.1.0",
    }


app.include_router(router)

if __name__ == '__main__':
    print("http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
