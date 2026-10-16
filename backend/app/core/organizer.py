import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import pymupdf as fitz

def merge_pdfs(file_paths: list[Path], output_path: Path) -> Path:
    """Merges multiple PDF documents in the order provided."""
    writer = PdfWriter()
    for fpath in file_paths:
        reader = PdfReader(str(fpath))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def parse_page_ranges(range_str: str, max_pages: int) -> list[list[int]]:
    """
    Parses ranges like '1-3, 5, 7-10' into list of 0-indexed page number groups.
    If 'all' or empty, splits every single page.
    """
    if not range_str or range_str.strip().lower() == "all":
        return [[i] for i in range(max_pages)]
    
    groups = []
    parts = range_str.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            match = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                start = max(1, start)
                end = min(max_pages, end)
                if start <= end:
                    groups.append([p - 1 for p in range(start, end + 1)])
        else:
            if part.isdigit():
                p = int(part)
                if 1 <= p <= max_pages:
                    groups.append([p - 1])
    return groups

def split_pdf(file_path: Path, ranges: str, output_dir: Path) -> list[Path]:
    """Splits a PDF by specified ranges or separates each page into its own file."""
    reader = PdfReader(str(file_path))
    total_pages = len(reader.pages)
    groups = parse_page_ranges(ranges, total_pages)
    
    output_files = []
    base_name = file_path.stem
    
    for idx, group in enumerate(groups, start=1):
        writer = PdfWriter()
        for p_idx in group:
            writer.add_page(reader.pages[p_idx])
        
        if len(group) == 1:
            part_name = f"{base_name}_sayfa_{group[0] + 1}.pdf"
        else:
            part_name = f"{base_name}_bolum_{idx}_sayfalar_{group[0]+1}-{group[-1]+1}.pdf"
            
        out_file = output_dir / part_name
        with open(out_file, "wb") as f_out:
            writer.write(f_out)
        output_files.append(out_file)
        
    return output_files

def extract_pages(file_path: Path, pages_1based: list[int], output_path: Path) -> Path:
    """Extracts chosen 1-based page numbers into a single new PDF."""
    reader = PdfReader(str(file_path))
    total_pages = len(reader.pages)
    writer = PdfWriter()
    
    for p in pages_1based:
        p_idx = p - 1
        if 0 <= p_idx < total_pages:
            writer.add_page(reader.pages[p_idx])
            
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def remove_pages(file_path: Path, pages_to_remove_1based: list[int], output_path: Path) -> Path:
    """Removes chosen 1-based pages and writes remaining pages."""
    remove_set = set(p - 1 for p in pages_to_remove_1based)
    reader = PdfReader(str(file_path))
    writer = PdfWriter()
    
    for idx, page in enumerate(reader.pages):
        if idx not in remove_set:
            writer.add_page(page)
            
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def organize_and_rotate_pages(file_path: Path, page_instructions: list[dict], output_path: Path) -> Path:
    """
    Applies custom visual order, rotation and page selection.
    page_instructions: list of dicts: [{'page_index': 0, 'rotation': 90}, ...]
    """
    reader = PdfReader(str(file_path))
    total_pages = len(reader.pages)
    writer = PdfWriter()
    
    for item in page_instructions:
        p_idx = int(item.get("page_index", 0))
        rot = int(item.get("rotation", 0))
        if 0 <= p_idx < total_pages:
            page = reader.pages[p_idx]
            if rot != 0:
                page.rotate(rot)
            writer.add_page(page)
            
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path

def rotate_all_pages(file_path: Path, angle: int, output_path: Path) -> Path:
    """Rotates all pages in the PDF by angle degrees (90, 180, 270)."""
    doc = fitz.open(str(file_path))
    for page in doc:
        page.set_rotation((page.rotation + angle) % 360)
    doc.save(str(output_path), garbage=3, deflate=True)
    doc.close()
    return output_path

def strip_pdf_metadata(file_path: Path, output_path: Path) -> Path:
    """Scans and scrubs all author, producer, title, and tracking metadata."""
    doc = fitz.open(str(file_path))
    empty_meta = {
        "title": "",
        "author": "",
        "subject": "",
        "keywords": "",
        "creator": "",
        "producer": "",
        "creationDate": "",
        "modDate": "",
        "trapped": ""
    }
    doc.set_metadata(empty_meta)
    doc.save(str(output_path), garbage=4, clean=True, deflate=True)
    doc.close()
    return output_path

