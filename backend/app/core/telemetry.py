import os
import json
import time
import sqlite3
import re
from pathlib import Path
from threading import Lock
from typing import Dict, Any

STATS_FILE = Path(__file__).resolve().parent.parent.parent / "stats.json"
DB_FILE = Path(__file__).resolve().parent.parent.parent / "telemetry.db"
_lock = Lock()

# Check for external Cloud Database (e.g. Supabase, Neon, Render PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

def _parse_user_agent(ua: str) -> Dict[str, str]:
    """Extracts device brand, model, OS, and browser from User-Agent string."""
    if not ua:
        return {"brand": "Unknown", "model": "Unknown", "os": "Unknown", "browser": "Unknown"}

    brand = "Diğer"
    model = "Cihaz"
    os_name = "Bilinmeyen OS"
    browser = "Bilinmeyen Tarayıcı"

    # Brand & Model
    if re.search(r"iPhone", ua, re.I):
        brand = "Apple"
        model = "iPhone"
        os_name = "iOS"
    elif re.search(r"iPad", ua, re.I):
        brand = "Apple"
        model = "iPad"
        os_name = "iPadOS"
    elif re.search(r"Macintosh|Mac OS X", ua, re.I):
        brand = "Apple"
        model = "Mac"
        os_name = "macOS"
    elif re.search(r"Samsung|SM-[A-Z0-9]+", ua, re.I):
        brand = "Samsung"
        match = re.search(r"SM-([A-Z0-9]+)", ua, re.I)
        model = f"Galaxy {match.group(1)}" if match else "Galaxy"
        os_name = "Android"
    elif re.search(r"Redmi|POCO|Mi [0-9]|Xiaomi", ua, re.I):
        brand = "Xiaomi"
        model = "Redmi" if "Redmi" in ua else ("POCO" if "POCO" in ua else "Xiaomi")
        os_name = "Android"
    elif re.search(r"Huawei|HONOR", ua, re.I):
        brand = "Huawei"
        model = "Huawei / Honor"
        os_name = "Android"
    elif re.search(r"Pixel", ua, re.I):
        brand = "Google"
        model = "Pixel"
        os_name = "Android"
    elif re.search(r"Windows", ua, re.I):
        brand = "Windows"
        model = "PC"
        os_name = "Windows"
    elif re.search(r"Linux", ua, re.I):
        brand = "Linux"
        model = "Workstation"
        os_name = "Linux"

    # Browser
    if "Edg" in ua:
        browser = "Edge"
    elif "Chrome" in ua:
        browser = "Chrome"
    elif "Safari" in ua and "Chrome" not in ua:
        browser = "Safari"
    elif "Firefox" in ua:
        browser = "Firefox"
    elif "Opera" in ua or "OPR" in ua:
        browser = "Opera"

    return {"brand": brand, "model": model, "os": os_name, "browser": browser}

def _init_sqlite():
    """Initializes SQLite telemetry tables if not existing."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id TEXT,
                    file_size_bytes INTEGER,
                    duration_ms INTEGER,
                    device_brand TEXT,
                    device_model TEXT,
                    os_name TEXT,
                    browser TEXT,
                    country TEXT,
                    created_at REAL
                )
            """)
            cursor.execute("PRAGMA journal_mode=WAL;")
            conn.commit()
    except Exception:
        pass

# Initialize local DB on module import
_init_sqlite()

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
        "devices": {},
        "countries": {},
        "created_at": time.time()
    }

def _save_stats(data: dict):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def track_operation(
    tool_id: str,
    file_size_bytes: int = 0,
    duration_ms: int = 0,
    user_agent: str = "",
    country: str = "TR"
):
    """
    Anonymously logs operation counters and device intelligence
    to SQLite and stats.json (or PostgreSQL if DATABASE_URL is set).
    """
    device_info = _parse_user_agent(user_agent)
    
    # 1. Update In-Memory / File Stats
    with _lock:
        stats = _load_stats()
        stats["total_operations"] = stats.get("total_operations", 0) + 1
        stats["total_bytes_processed"] = stats.get("total_bytes_processed", 0) + file_size_bytes
        
        # Tools distribution
        tools_map = stats.get("tools_usage", {})
        tools_map[tool_id] = tools_map.get(tool_id, 0) + 1
        stats["tools_usage"] = tools_map
        
        # Device distribution
        dev_map = stats.get("devices", {})
        b = device_info["brand"]
        dev_map[b] = dev_map.get(b, 0) + 1
        stats["devices"] = dev_map
        
        # Country distribution
        c_map = stats.get("countries", {})
        c = (country or "TR").upper()
        c_map[c] = c_map.get(c, 0) + 1
        stats["countries"] = c_map
        
        stats["last_operation_time"] = time.time()
        _save_stats(stats)

    # 2. Insert record into SQLite DB
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO operations (
                    tool_id, file_size_bytes, duration_ms,
                    device_brand, device_model, os_name, browser, country, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tool_id,
                file_size_bytes,
                duration_ms,
                device_info["brand"],
                device_info["model"],
                device_info["os"],
                device_info["browser"],
                country,
                time.time()
            ))
            conn.commit()
    except Exception:
        pass

def get_telemetry_summary() -> dict:
    """Returns aggregated anonymous statistics and device breakdown."""
    with _lock:
        stats = _load_stats()
        mb = round(stats.get("total_bytes_processed", 0) / (1024 * 1024), 2)
        
        # Pull latest 10 operations from SQLite if available
        recent_ops = []
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tool_id, file_size_bytes, duration_ms, device_brand, country, created_at
                    FROM operations ORDER BY id DESC LIMIT 10
                """)
                for row in cursor.fetchall():
                    recent_ops.append({
                        "tool": row[0],
                        "size_kb": round(row[1] / 1024, 1),
                        "duration_ms": row[2],
                        "brand": row[3],
                        "country": row[4],
                        "time": time.strftime("%H:%M:%S", time.localtime(row[5]))
                    })
        except Exception:
            pass

        return {
            "total_operations": stats.get("total_operations", 0),
            "total_mb_processed": mb,
            "tools_usage": stats.get("tools_usage", {}),
            "devices": stats.get("devices", {}),
            "countries": stats.get("countries", {}),
            "recent_operations": recent_ops,
            "cloud_db_connected": bool(DATABASE_URL)
        }
