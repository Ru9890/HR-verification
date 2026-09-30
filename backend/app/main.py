from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import verify, reports, settings as settings_router, samples

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Resume Evidence Verification Engine — Corroborates claims against public GitHub, Portfolio, and Web evidence.",
    lifespan=lifespan
)

# CORS — allow any origin (wildcard) without credentials.
# NOTE: allow_credentials=True + allow_origins=["*"] is rejected by browsers;
# use explicit origins list if credentials are ever needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # must be False when origins="*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register routers
app.include_router(verify.router)
app.include_router(reports.router)
app.include_router(samples.router)
app.include_router(settings_router.router)

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
