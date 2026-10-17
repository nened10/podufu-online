from pathlib import Path
import io
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

def add_watermark_text(
    file_path: Path,
    output_path: Path,
    text: str,
    opacity: float = 0.25,
    rotation: int = 45,
    font_size: int = 42,
    color_hex: str = "#888888"
) -> Path:
    """Adds a semi-transparent text watermark across all pages using vector overlay."""
    reader = PdfReader(str(file_path))
    writer = PdfWriter()
    
    for page in reader.pages:
        packet = io.BytesIO()
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.saveState()
        can.translate(width / 2, height / 2)
        can.rotate(rotation)
        
        c = HexColor(color_hex)
        can.setFillColor(c, alpha=opacity)
        can.setFont("Helvetica-Bold", font_size)
        can.drawCentredString(0, 0, text)
        can.restoreState()
        can.save()
        
        packet.seek(0)
        wm_reader = PdfReader(packet)
        page.merge_page(wm_reader.pages[0])
        writer.add_page(page)
        
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def add_page_numbers(
    file_path: Path,
    output_path: Path,
    position: str = "bottom-center",
    format_pattern: str = "Sayfa {n} / {total}",
    font_size: int = 10,
    margin: int = 30
) -> Path:
    """Adds customizable page numbers to each page."""
    reader = PdfReader(str(file_path))
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    for idx, page in enumerate(reader.pages):
        packet = io.BytesIO()
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFont("Helvetica", font_size)
        can.setFillColor(HexColor("#333333"))
        
        text = format_pattern.replace("{n}", str(idx + 1)).replace("{total}", str(total_pages))
        
        # Calculate X & Y coordinates
        if "bottom" in position:
            y = margin
        else:
            y = height - margin
            
        if "center" in position:
            can.drawCentredString(width / 2, y, text)
        elif "right" in position:
            can.drawRightString(width - margin, y, text)
        else:  # left
            can.drawString(margin, y, text)
            
        can.save()
        packet.seek(0)
        num_reader = PdfReader(packet)
        page.merge_page(num_reader.pages[0])
        writer.add_page(page)
        
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def redact_text_occurrences(file_path: Path, output_path: Path, search_term: str) -> tuple[Path, int]:
    """
    Permanently erases sensitive terms from the PDF content stream.
    Replaces matched text with solid black box and strips text completely.
    Performs case-insensitive and multi-locale (e.g. Turkish) variant matching.
    """
    clean_term = search_term.strip()
    if not clean_term:
        raise ValueError("Sansürlenecek metin boş olamaz.")
        
    doc = fitz.open(file_path)
    total_redacted = 0

    # Build comprehensive case variants so 'gizli', 'GİZLİ', 'Gizli', 'secret', 'SECRET' all match
    variants = {clean_term, clean_term.lower(), clean_term.upper(), clean_term.title()}
    # Turkish-specific casing:
    tr_upper = str.maketrans({"i": "İ", "ı": "I"})
    tr_lower = str.maketrans({"İ": "i", "I": "ı"})
    variants.add(clean_term.translate(tr_upper).upper())
    variants.add(clean_term.translate(tr_lower).lower())
    # ASCII transliteration fallback:
    ascii_map = str.maketrans({
        "İ": "I", "ı": "i", "ş": "s", "Ş": "S",
        "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U",
        "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"
    })
    variants.add(clean_term.translate(ascii_map))
    variants.add(clean_term.translate(ascii_map).upper())
    variants.add(clean_term.translate(ascii_map).lower())
    search_variants = [v for v in variants if v]

    try:
        for page in doc:
            page_rects = []
            for v in search_variants:
                rects = page.search_for(v)
                for r in rects:
                    # Avoid duplicate overlapping redaction rectangles
                    if not any(r.intersects(existing) for existing in page_rects):
                        page_rects.append(r)
                        page.add_redact_annot(r, fill=(0, 0, 0))  # Black box
                        total_redacted += 1
            if page_rects:
                page.apply_redactions()
                
        doc.save(str(output_path))
        return output_path, total_redacted
    finally:
        doc.close()
