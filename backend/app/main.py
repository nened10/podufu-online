from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.config import FRONTEND_DIR, cleanup_old_workspaces

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run cleanup of any stale workspaces
    cleanup_old_workspaces()
    yield
    # Shutdown
    cleanup_old_workspaces()

app = FastAPI(
    title="Pödüfü.online",
    description="%100 Ücretsiz, güvenli ve hızlı PDF araçları platformu.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Yerel geliştirme ve yerel ağ erişimi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
from starlette.requests import Request
from app.core.telemetry import track_operation

@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method == "POST" and request.url.path.startswith("/api/"):
        endpoint = request.url.path.replace("/api/", "")
        if endpoint not in ["inspect"]:
            if response.status_code == 200:
                content_length = int(request.headers.get("content-length", 0))
                track_operation(endpoint, content_length)
    return response

app.include_router(api_router)

# Mount Frontend static files
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
