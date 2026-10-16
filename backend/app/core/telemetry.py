import json
import os
import threading
import time
import urllib.request
from pathlib import Path
from threading import Lock

STATS_FILE = Path(__file__).resolve().parent.parent.parent / "stats.json"
_lock = Lock()

# Cloud Database configuration (e.g. from Render Environment Variables)
# Mode 1: Supabase REST API (Free & Zero extra pip drivers required)
_raw_supabase_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
if _raw_supabase_url.endswith("/rest/v1"):
    _raw_supabase_url = _raw_supabase_url[:-8].rstrip("/")
SUPABASE_URL = _raw_supabase_url
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "podufu_telemetry").strip()

# Mode 2: Generic Cloud Webhook or Telemetry Ingest URL
TELEMETRY_WEBHOOK_URL = os.getenv("TELEMETRY_WEBHOOK_URL", "").strip()

def _load_local_stats() -> dict:
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_operations": 0,
        "total_bytes_processed": 0,
        "tools_usage": {},
        "funnel": {
            "page_views": 0,
            "files_selected": 0,
            "conversions_completed": 0,
            "downloads": 0
        },
        "devices": {"mobile": 0, "desktop": 0},
        "countries": {},
        "languages": {},
        "durations_sum": 0.0,
        "durations_count": 0,
        "created_at": time.time()
    }

def _save_local_stats(data: dict):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def _sync_to_cloud_database_async(tool_id: str, file_size_bytes: int):
    """Background thread to push anonymous telemetry to Cloud DB without blocking user."""
    def _worker():
        try:
            # 1. Supabase REST API support
            if SUPABASE_URL and SUPABASE_KEY:
                endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
                payload = json.dumps({
                    "tool_id": tool_id,
                    "bytes_processed": file_size_bytes,
                    "timestamp": time.time()
                }).encode("utf-8")
                
                req = urllib.request.Request(endpoint, data=payload, headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                })
                with urllib.request.urlopen(req, timeout=4) as _:
                    pass
            
            # 2. Generic Telemetry Webhook support
            elif TELEMETRY_WEBHOOK_URL:
                payload = json.dumps({
                    "event": "pdf_operation",
                    "tool_id": tool_id,
                    "bytes": file_size_bytes,
                    "timestamp": time.time()
                }).encode("utf-8")
                
                req = urllib.request.Request(TELEMETRY_WEBHOOK_URL, data=payload, headers={
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=4) as _:
                    pass
        except Exception:
            # Telemetry errors must never disrupt user operations
            pass

    threading.Thread(target=_worker, daemon=True).start()

def _sync_client_event_to_cloud_async(event_name: str, payload_dict: dict):
    """Push client beacon event to Supabase or Webhook."""
    def _worker():
        try:
            if SUPABASE_URL and SUPABASE_KEY:
                endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
                p = json.dumps({
                    "tool_id": f"event:{event_name}",
                    "bytes_processed": int(payload_dict.get("data", {}).get("file_size_mb", 0) * 1024 * 1024),
                    "timestamp": time.time()
                }).encode("utf-8")
                req = urllib.request.Request(endpoint, data=p, headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                })
                with urllib.request.urlopen(req, timeout=4) as _:
                    pass
            elif TELEMETRY_WEBHOOK_URL:
                p = json.dumps(payload_dict).encode("utf-8")
                req = urllib.request.Request(TELEMETRY_WEBHOOK_URL, data=p, headers={
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=4) as _:
                    pass
        except Exception:
            pass
            
    threading.Thread(target=_worker, daemon=True).start()

def track_operation(tool_id: str, file_size_bytes: int = 0):
    """Anonymously increments operation counters for server-side PDF processing."""
    with _lock:
        stats = _load_local_stats()
        stats["total_operations"] = stats.get("total_operations", 0) + 1
        stats["total_bytes_processed"] = stats.get("total_bytes_processed", 0) + file_size_bytes
        
        tools_map = stats.get("tools_usage", {})
        tools_map[tool_id] = tools_map.get(tool_id, 0) + 1
        stats["tools_usage"] = tools_map
        stats["last_operation_time"] = time.time()
        
        _save_local_stats(stats)
        
    if (SUPABASE_URL and SUPABASE_KEY) or TELEMETRY_WEBHOOK_URL:
        _sync_to_cloud_database_async(tool_id, file_size_bytes)

def track_client_telemetry(payload: dict):
    """Processes client-side telemetry beacons (page view, drop-off funnel, device specs)."""
    event = payload.get("event", "unknown")
    device = payload.get("device", {})
    geo_country = payload.get("geo_country", "unknown")
    data = payload.get("data", {})
    
    with _lock:
        stats = _load_local_stats()
        funnel = stats.setdefault("funnel", {
            "page_views": 0,
            "files_selected": 0,
            "conversions_completed": 0,
            "downloads": 0
        })
        
        if event == "page_view":
            funnel["page_views"] = funnel.get("page_views", 0) + 1
        elif event == "file_selected":
            funnel["files_selected"] = funnel.get("files_selected", 0) + 1
        elif event == "conversion_success":
            funnel["conversions_completed"] = funnel.get("conversions_completed", 0) + 1
            dur = float(data.get("duration_seconds", 0))
            if dur > 0:
                stats["durations_sum"] = stats.get("durations_sum", 0.0) + dur
                stats["durations_count"] = stats.get("durations_count", 0) + 1
        elif event == "file_downloaded":
            funnel["downloads"] = funnel.get("downloads", 0) + 1
            
        # Device tracking
        devices = stats.setdefault("devices", {"mobile": 0, "desktop": 0})
        if device.get("is_mobile"):
            devices["mobile"] = devices.get("mobile", 0) + 1
        else:
            devices["desktop"] = devices.get("desktop", 0) + 1
            
        # Language tracking
        lang = str(device.get("lang", "unknown"))[:2].lower()
        if lang:
            languages = stats.setdefault("languages", {})
            languages[lang] = languages.get(lang, 0) + 1
            
        # Country tracking
        if geo_country and geo_country != "unknown":
            countries = stats.setdefault("countries", {})
            countries[geo_country] = countries.get(geo_country, 0) + 1
            
        _save_local_stats(stats)
        
    if (SUPABASE_URL and SUPABASE_KEY) or TELEMETRY_WEBHOOK_URL:
        _sync_client_event_to_cloud_async(event, payload)

def get_telemetry_summary() -> dict:
    """Returns aggregated anonymous statistics including conversion funnel."""
    with _lock:
        stats = _load_local_stats()
        mb = round(stats.get("total_bytes_processed", 0) / (1024 * 1024), 2)
        funnel = stats.get("funnel", {
            "page_views": 0,
            "files_selected": 0,
            "conversions_completed": 0,
            "downloads": 0
        })
        pv = funnel.get("page_views", 0)
        dl = funnel.get("downloads", 0)
        conv_rate = f"{round((dl / pv) * 100, 1)}%" if pv > 0 else "0.0%"
        
        dur_sum = stats.get("durations_sum", 0.0)
        dur_count = stats.get("durations_count", 0)
        avg_dur = round(dur_sum / dur_count, 2) if dur_count > 0 else 0.0
        
        return {
            "total_operations": stats.get("total_operations", 0),
            "total_mb_processed": mb,
            "conversion_funnel": funnel,
            "download_conversion_rate": conv_rate,
            "average_processing_duration_sec": avg_dur,
            "devices": stats.get("devices", {"mobile": 0, "desktop": 0}),
            "top_languages": stats.get("languages", {}),
            "top_countries": stats.get("countries", {}),
            "tools_usage": stats.get("tools_usage", {}),
            "cloud_db_enabled": bool((SUPABASE_URL and SUPABASE_KEY) or TELEMETRY_WEBHOOK_URL)
        }
