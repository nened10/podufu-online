import os
import re
import shutil
import zipfile
from pathlib import Path
from fastapi import UploadFile

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename removing hazardous path characters."""
    base = os.path.basename(filename)
    clean = re.sub(r'[\\/*?:"<>|]', "", base)
    return clean or "document.pdf"

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """Safely saves an uploaded file in chunks to prevent memory bloat."""
    with open(destination, "wb") as buffer:
        while content := await upload_file.read(1024 * 1024):  # 1MB chunk
            buffer.write(content)
    return destination

def create_zip_archive(source_files: list[Path], output_zip_path: Path) -> Path:
    """Packages multiple files into a single ZIP archive."""
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in source_files:
            if file.exists() and file.is_file():
                zipf.write(file, arcname=file.name)
    return output_zip_path
