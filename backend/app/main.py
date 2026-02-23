from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth_router, user_router, admin_router, test_series_router, attempt_router, payment_router
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create missing database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace abstract with true domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(user_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(admin_router.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(test_series_router.router, prefix=f"{settings.API_V1_STR}/tests", tags=["test-series"])
app.include_router(attempt_router.router, prefix=f"{settings.API_V1_STR}/attempts", tags=["attempts"])
app.include_router(payment_router.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
