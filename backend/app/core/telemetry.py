import json
import time
from pathlib import Path
from threading import Lock

STATS_FILE = Path(__file__).resolve().parent.parent.parent / "stats.json"
_lock = Lock()

def _load_stats() -> dict:
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

def _save_stats(data: dict):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def track_operation(tool_id: str, file_size_bytes: int = 0):
    """Anonymously increments operation counters for product telemetry."""
    with _lock:
        stats = _load_stats()
        stats["total_operations"] = stats.get("total_operations", 0) + 1
        stats["total_bytes_processed"] = stats.get("total_bytes_processed", 0) + file_size_bytes
        
        tools_map = stats.get("tools_usage", {})
        tools_map[tool_id] = tools_map.get(tool_id, 0) + 1
        stats["tools_usage"] = tools_map
        stats["last_operation_time"] = time.time()
        
        _save_stats(stats)

def get_telemetry_summary() -> dict:
    """Returns aggregated anonymous statistics."""
    with _lock:
        stats = _load_stats()
        mb = round(stats.get("total_bytes_processed", 0) / (1024 * 1024), 2)
        return {
            "total_operations": stats.get("total_operations", 0),
            "total_mb_processed": mb,
            "tools_usage": stats.get("tools_usage", {})
        }
