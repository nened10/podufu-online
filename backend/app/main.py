import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.config import FRONTEND_DIR, cleanup_old_workspaces
from app.core.telemetry import track_operation

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

# Multi-language i18n & SEO Routing
SUPPORTED_LANGS = {"en", "de", "es", "fr", "pt", "tr"}
LOCALES_DIR = FRONTEND_DIR / "locales"
INDEX_HTML_PATH = FRONTEND_DIR / "index.html"

def render_localized_index(lang: str = "en") -> HTMLResponse:
    if not INDEX_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
        
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    
    locale_file = LOCALES_DIR / f"{lang}.json"
    if locale_file.exists():
        try:
            with open(locale_file, "r", encoding="utf-8") as f:
                loc = json.load(f)
                meta_title = loc.get("meta", {}).get("title", "Pödüfü 💜")
                meta_desc = loc.get("meta", {}).get("description", "")
                
                # Replace html lang & title
                html = html.replace('<html lang="en"', f'<html lang="{lang}"')
                html = html.replace('<title>Pödüfü 💜</title>', f'<title>{meta_title}</title>')
                
                # Canonical & hreflang injections
                hreflang_tags = f'''  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="https://podufu.onrender.com/{lang}/" />
  <link rel="alternate" hreflang="en" href="https://podufu.onrender.com/en/" />
  <link rel="alternate" hreflang="de" href="https://podufu.onrender.com/de/" />
  <link rel="alternate" hreflang="es" href="https://podufu.onrender.com/es/" />
  <link rel="alternate" hreflang="fr" href="https://podufu.onrender.com/fr/" />
  <link rel="alternate" hreflang="pt" href="https://podufu.onrender.com/pt/" />
  <link rel="alternate" hreflang="tr" href="https://podufu.onrender.com/tr/" />
  <link rel="alternate" hreflang="x-default" href="https://podufu.onrender.com/en/" />'''
                html = html.replace('<!-- SEO_HREFLANG_PLACEHOLDER -->', hreflang_tags)
        except Exception:
            pass

    return HTMLResponse(content=html, media_type="text/html")

@app.get("/")
async def root_index(request: Request):
    # Detect browser accept-language if visiting root directly
    accept_lang = request.headers.get("accept-language", "").lower()
    detected = "en"
    for l in ["de", "es", "fr", "pt", "tr"]:
        if accept_lang.startswith(l) or f",{l}" in accept_lang or f";{l}" in accept_lang:
            detected = l
            break
    return render_localized_index(detected)

@app.get("/{lang}")
@app.get("/{lang}/")
async def lang_index(lang: str):
    if lang in SUPPORTED_LANGS:
        return render_localized_index(lang)
    # Check if a static file in root exists (e.g. favicon.ico)
    static_file = FRONTEND_DIR / lang
    if static_file.is_file():
        return FileResponse(static_file)
    raise HTTPException(status_code=404)

# Mount static subdirectories
if FRONTEND_DIR.exists():
    for sub in ["css", "js", "assets", "locales"]:
        sub_dir = FRONTEND_DIR / sub
        if sub_dir.exists():
            app.mount(f"/{sub}", StaticFiles(directory=str(sub_dir)), name=sub)
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="frontend")
