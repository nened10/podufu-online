import pymupdf as fitz
from pathlib import Path

def inspect_pdf(file_path: Path) -> dict:
    """Extracts structural metadata, page count, and dimensions of a PDF."""
    doc = fitz.open(file_path)
    try:
        is_encrypted = doc.is_encrypted
        page_count = len(doc)
        meta = doc.metadata or {}
        
        pages_info = []
        # If encrypted, pages cannot be loaded without a password
        if not is_encrypted:
            for i in range(min(page_count, 100)):
                try:
                    page = doc[i]
                    rect = page.rect
                    pages_info.append({
                        "page_number": i + 1,
                        "width": round(rect.width, 2),
                        "height": round(rect.height, 2),
                        "rotation": page.rotation
                    })
                except Exception:
                    break

        return {
            "page_count": page_count,
            "is_encrypted": is_encrypted,
            "title": meta.get("title", "") or "",
            "author": meta.get("author", "") or "",
            "subject": meta.get("subject", "") or "",
            "keywords": meta.get("keywords", "") or "",
            "creator": meta.get("creator", "") or "",
            "producer": meta.get("producer", "") or "",
            "format": doc.pdf_version() if hasattr(doc, "pdf_version") else "1.7",
            "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "pages": pages_info
        }
    finally:
        doc.close()

def render_page_thumbnail(file_path: Path, page_index: int, output_img_path: Path, max_width: int = 300) -> Path:
    """Renders a specific page to a PNG thumbnail using high-speed PyMuPDF rasterization."""
    doc = fitz.open(file_path)
    try:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError("Page index out of range")
        
        page = doc[page_index]
        rect = page.rect
        scale = max_width / rect.width if rect.width > 0 else 1.0
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(output_img_path)
        return output_img_path
    finally:
        doc.close()
