import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.config import FRONTEND_DIR, cleanup_old_workspaces
from app.core.telemetry import track_operation, track_client_telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_old_workspaces()
    yield
    cleanup_old_workspaces()

app = FastAPI(
    title="Pödüfü.online",
    description="%100 Ücretsiz, güvenli ve hızlı PDF araçları platformu.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
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
        if endpoint not in ["inspect", "telemetry"]:
            if response.status_code == 200:
                content_length = int(request.headers.get("content-length", 0))
                track_operation(endpoint, content_length)
    return response

app.include_router(api_router)

# Mount static subdirectories FIRST so /css, /js, /assets, /locales are served immediately
if FRONTEND_DIR.exists():
    for sub in ["css", "js", "assets", "locales"]:
        sub_dir = FRONTEND_DIR / sub
        if sub_dir.exists():
            app.mount(f"/{sub}", StaticFiles(directory=str(sub_dir)), name=sub)

# Native Client Telemetry Beacon Endpoint
@app.post("/api/telemetry")
async def client_telemetry_beacon(request: Request):
    """Zero-cookie, non-blocking client telemetry beacon."""
    try:
        body = await request.json()
        country = request.headers.get("cf-ipcountry", "unknown")
        body["geo_country"] = country
        track_client_telemetry(body)
    except Exception:
        pass
    return Response(status_code=204)

# Multi-language i18n & Global SEO Routing (9 languages x 19 tools)
SUPPORTED_LANGS = {"en", "de", "es", "fr", "pt", "tr", "ru", "ja", "ar"}
VALID_TOOL_IDS = {
    "merge", "split", "organize", "compress",
    "word-to-pdf", "ppt-to-pdf", "excel-to-pdf", "pdf-to-word",
    "images-to-pdf", "pdf-to-images", "pdf-to-text",
    "protect", "unlock", "watermark", "page-numbers",
    "redact", "repair", "rotate", "metadata"
}

LOCALES_DIR = FRONTEND_DIR / "locales"
INDEX_HTML_PATH = FRONTEND_DIR / "index.html"

def render_localized_index(lang: str = "en", tool_id: str | None = None) -> HTMLResponse:
    if not INDEX_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
        
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    if lang not in SUPPORTED_LANGS:
        lang = "en"
        
    locale_file = LOCALES_DIR / f"{lang}.json"
    if locale_file.exists():
        try:
            with open(locale_file, "r", encoding="utf-8") as f:
                loc = json.load(f)
                
                if tool_id and tool_id in VALID_TOOL_IDS:
                    tool_data = loc.get("tools", {}).get(tool_id, {})
                    tool_title = tool_data.get("title", tool_id)
                    tool_desc = tool_data.get("description", "")
                    
                    page_title = f"{tool_title} - Pödüfü 💜"
                    page_desc = f"{tool_title}: {tool_desc} - 100% Free, Private & Secure Online PDF Tools."
                    canonical_url = f"https://podufu.onrender.com/{lang}/{tool_id}"
                    
                    html = html.replace('<html lang="en"', f'<html lang="{lang}"')
                    html = html.replace('<title>Pödüfü 💜</title>', f'<title>{page_title}</title>')
                    
                    hreflang_lines = [f'  <meta name="description" content="{page_desc}">']
                    hreflang_lines.append(f'  <link rel="canonical" href="{canonical_url}" />')
                    for l in ["en", "de", "es", "fr", "pt", "tr", "ru", "ja", "ar"]:
                        hreflang_lines.append(f'  <link rel="alternate" hreflang="{l}" href="https://podufu.onrender.com/{l}/{tool_id}" />')
                    hreflang_lines.append(f'  <link rel="alternate" hreflang="x-default" href="https://podufu.onrender.com/en/{tool_id}" />')
                    
                    tool_schema = f'''  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{
        "@type": "ListItem",
        "position": 1,
        "name": "Pödüfü",
        "item": "https://podufu.onrender.com/{lang}/"
      }},
      {{
        "@type": "ListItem",
        "position": 2,
        "name": "{tool_title}",
        "item": "{canonical_url}"
      }}
    ]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "{tool_title} | Pödüfü",
    "url": "{canonical_url}",
    "description": "{tool_desc}",
    "applicationCategory": "UtilitiesApplication",
    "operatingSystem": "All",
    "offers": {{
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }}
  }}
  </script>'''
                    hreflang_lines.append(tool_schema)
                    html = html.replace('<!-- SEO_HREFLANG_PLACEHOLDER -->', "\n".join(hreflang_lines))
                    html = html.replace('content="https://podufu.onrender.com/"', f'content="{canonical_url}"')
                    html = html.replace('content="Pödüfü 💜 - 100% Free, Secure & Fast Online PDF Tools"', f'content="{page_title}"')
                    html = html.replace('content="Merge, split, compress, convert, protect, unlock and edit PDFs online for free. Fast, 100% private with no file size limits."', f'content="{page_desc}"')
                else:
                    meta_title = loc.get("meta", {}).get("title", "Pödüfü 💜")
                    meta_desc = loc.get("meta", {}).get("description", "")
                    canonical_url = f"https://podufu.onrender.com/{lang}/"
                    
                    html = html.replace('<html lang="en"', f'<html lang="{lang}"')
                    html = html.replace('<title>Pödüfü 💜</title>', f'<title>{meta_title}</title>')
                    
                    hreflang_lines = [f'  <meta name="description" content="{meta_desc}">']
                    hreflang_lines.append(f'  <link rel="canonical" href="{canonical_url}" />')
                    for l in ["en", "de", "es", "fr", "pt", "tr", "ru", "ja", "ar"]:
                        hreflang_lines.append(f'  <link rel="alternate" hreflang="{l}" href="https://podufu.onrender.com/{l}/" />')
                    hreflang_lines.append(f'  <link rel="alternate" hreflang="x-default" href="https://podufu.onrender.com/en/" />')
                    
                    top_tools = ["merge", "compress", "pdf-to-word", "word-to-pdf", "split", "protect", "rotate", "metadata"]
                    sitelinks_items = []
                    for idx, t_id in enumerate(top_tools, start=1):
                        t_name = loc.get("tools", {}).get(t_id, {}).get("title", t_id)
                        sitelinks_items.append(f'''      {{
        "@type": "SiteNavigationElement",
        "position": {idx},
        "name": "{t_name}",
        "url": "https://podufu.onrender.com/{lang}/{t_id}"
      }}''')
                    
                    items_joined = ",\n".join(sitelinks_items)
                    sitelinks_schema = f'''  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Pödüfü PDF Tools",
    "itemListElement": [
{items_joined}
    ]
  }}
  </script>'''
                    hreflang_lines.append(sitelinks_schema)
                    html = html.replace('<!-- SEO_HREFLANG_PLACEHOLDER -->', "\n".join(hreflang_lines))
                    html = html.replace('content="https://podufu.onrender.com/"', f'content="{canonical_url}"')
        except Exception as e:
            print("Localization injection error:", e)

    return HTMLResponse(content=html, media_type="text/html")

# Static SEO & AI agent files
@app.get("/robots.txt")
async def robots_txt():
    p = FRONTEND_DIR / "robots.txt"
    if p.exists():
        return FileResponse(p, media_type="text/plain")
    raise HTTPException(status_code=404)

@app.get("/sitemap.xml")
async def sitemap_xml():
    p = FRONTEND_DIR / "sitemap.xml"
    if p.exists():
        content = p.read_bytes()
        return Response(
            content=content,
            media_type="application/xml; charset=utf-8",
            headers={
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "public, max-age=3600"
            }
        )
    raise HTTPException(status_code=404)

@app.get("/llms.txt")
async def llms_txt():
    p = FRONTEND_DIR / "llms.txt"
    if p.exists():
        return FileResponse(p, media_type="text/plain")
    raise HTTPException(status_code=404)

@app.get("/")
async def root_index(request: Request):
    accept_lang = request.headers.get("accept-language", "").lower()
    detected = "en"
    for l in ["de", "es", "fr", "pt", "tr", "ru", "ja", "ar"]:
        if accept_lang.startswith(l) or f",{l}" in accept_lang or f";{l}" in accept_lang:
            detected = l
            break
    return render_localized_index(detected)

@app.get("/{lang_or_tool}")
@app.get("/{lang_or_tool}/")
async def lang_or_tool_index(lang_or_tool: str, request: Request):
    if lang_or_tool in SUPPORTED_LANGS:
        return render_localized_index(lang_or_tool)
    if lang_or_tool in VALID_TOOL_IDS:
        accept_lang = request.headers.get("accept-language", "").lower()
        detected = "en"
        for l in ["de", "es", "fr", "pt", "tr", "ru", "ja", "ar"]:
            if accept_lang.startswith(l) or f",{l}" in accept_lang or f";{l}" in accept_lang:
                detected = l
                break
        return render_localized_index(detected, tool_id=lang_or_tool)
    static_file = FRONTEND_DIR / lang_or_tool
    if static_file.is_file():
        return FileResponse(static_file)
    raise HTTPException(status_code=404)

@app.get("/{lang}/{tool}")
@app.get("/{lang}/{tool}/")
async def localized_tool_index(lang: str, tool: str):
    if lang in SUPPORTED_LANGS and tool in VALID_TOOL_IDS:
        return render_localized_index(lang, tool_id=tool)
    static_file = FRONTEND_DIR / lang / tool
    if static_file.is_file():
        return FileResponse(static_file)
    raise HTTPException(status_code=404)

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="frontend")
