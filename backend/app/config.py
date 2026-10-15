import os
import shutil
import tempfile
import time
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMP_WORKSPACE_DIR = BASE_DIR / "temp_workspace"

TEMP_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

# File settings
MAX_UPLOAD_SIZE_MB = 500  # 500 MB per file
CLEANUP_TTL_SECONDS = 3600  # Clean temp files older than 1 hour

def create_job_workspace(job_id: str) -> Path:
    """Creates an isolated temporary directory for a specific job."""
    job_dir = TEMP_WORKSPACE_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir

def cleanup_old_workspaces():
    """Removes temporary job workspaces older than CLEANUP_TTL_SECONDS."""
    now = time.time()
    if not TEMP_WORKSPACE_DIR.exists():
        return
    for item in TEMP_WORKSPACE_DIR.iterdir():
        if item.is_dir():
            try:
                mtime = item.stat().st_mtime
                if now - mtime > CLEANUP_TTL_SECONDS:
                    shutil.rmtree(item, ignore_errors=True)
            except Exception:
                pass
