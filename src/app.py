import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routers import auth
from api.routers import translate
from core.config import settings
from core.database import Base
from core.database import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Add Session Middleware (Required for Authlib OAuth flow to store state/nonce)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(translate.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Zack Zack Deutsch Backend"}


if __name__ == '__main__':
    print("http://localhost:8080/docs")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
