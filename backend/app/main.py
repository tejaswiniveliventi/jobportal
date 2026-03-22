from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import create_tables
from app.routers import auth, profile, applications, jobs

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting — creating tables...")
    await create_tables()
    logger.info("DB ready.")
    yield
    logger.info("Shutdown.")


app = FastAPI(
    title="Job Portal API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

P = "/api/v1"
app.include_router(auth.router,         prefix=P)
app.include_router(profile.router,      prefix=P)
app.include_router(applications.router, prefix=P)
app.include_router(jobs.router,         prefix=P)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
