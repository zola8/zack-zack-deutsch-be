from fastapi import APIRouter

router = APIRouter(prefix="/translate", tags=["Translate"])


@router.get("/")
async def homepage():
    return {
        "version": "0.1.0",
    }
