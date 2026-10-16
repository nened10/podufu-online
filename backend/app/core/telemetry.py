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
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "podufu_telemetry")

# Mode 2: Generic Cloud Webhook or Telemetry Ingest URL
TELEMETRY_WEBHOOK_URL = os.getenv("TELEMETRY_WEBHOOK_URL", "")

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

def track_operation(tool_id: str, file_size_bytes: int = 0):
    """Anonymously increments operation counters for product telemetry."""
    with _lock:
        stats = _load_local_stats()
        stats["total_operations"] = stats.get("total_operations", 0) + 1
        stats["total_bytes_processed"] = stats.get("total_bytes_processed", 0) + file_size_bytes
        
        tools_map = stats.get("tools_usage", {})
        tools_map[tool_id] = tools_map.get(tool_id, 0) + 1
        stats["tools_usage"] = tools_map
        stats["last_operation_time"] = time.time()
        
        _save_local_stats(stats)
        
    # Trigger non-blocking cloud database sync if configured
    if (SUPABASE_URL and SUPABASE_KEY) or TELEMETRY_WEBHOOK_URL:
        _sync_to_cloud_database_async(tool_id, file_size_bytes)

def get_telemetry_summary() -> dict:
    """Returns aggregated anonymous statistics."""
    with _lock:
        stats = _load_local_stats()
        mb = round(stats.get("total_bytes_processed", 0) / (1024 * 1024), 2)
        return {
            "total_operations": stats.get("total_operations", 0),
            "total_mb_processed": mb,
            "tools_usage": stats.get("tools_usage", {}),
            "cloud_db_enabled": bool((SUPABASE_URL and SUPABASE_KEY) or TELEMETRY_WEBHOOK_URL)
        }

