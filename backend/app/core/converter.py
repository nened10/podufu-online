import os
import subprocess
import sys
from pathlib import Path
from PIL import Image
import pymupdf as fitz
from pdf2docx import Converter

def images_to_pdf(image_paths: list[Path], output_path: Path) -> Path:
    """Converts a sequence of images (PNG, JPG, BMP, WEBP) into a single PDF."""
    if not image_paths:
        raise ValueError("En az bir görsel seçilmelidir.")
    
    pil_images = []
    for img_path in image_paths:
        img = Image.open(img_path)
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            pil_images.append(rgb_img)
        else:
            pil_images.append(img.convert("RGB"))
            
    first_image = pil_images[0]
    additional_images = pil_images[1:] if len(pil_images) > 1 else []
    
    first_image.save(
        output_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=additional_images
    )
    return output_path

def pdf_to_images(file_path: Path, output_dir: Path, dpi: int = 200, img_format: str = "png") -> list[Path]:
    """Converts every page of a PDF into high-quality image files."""
    doc = fitz.open(file_path)
    output_images = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    base_name = file_path.stem
    
    try:
        for idx, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_path = output_dir / f"{base_name}_sayfa_{idx + 1}.{img_format}"
            pix.save(img_path)
            output_images.append(img_path)
        return output_images
    finally:
        doc.close()

def pdf_to_docx_file(file_path: Path, output_path: Path) -> Path:
    """Converts a PDF to a formatted, editable Microsoft Word (.docx) document."""
    cv = Converter(str(file_path))
    try:
        cv.convert(str(output_path), start=0, end=None)
        return output_path
    finally:
        cv.close()

def pdf_to_markdown_or_text(file_path: Path, output_path: Path) -> Path:
    """Extracts structured text / markdown content from PDF."""
    doc = fitz.open(file_path)
    try:
        content_parts = []
        for idx, page in enumerate(doc):
            content_parts.append(f"<!-- Sayfa {idx + 1} -->\n")
            text = page.get_text("text")
            content_parts.append(text)
            content_parts.append("\n\n---\n\n")
            
        full_text = "".join(content_parts)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        return output_path
    finally:
        doc.close()

def word_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Converts DOCX / DOC to PDF with 100% native layout fidelity."""
    input_str = str(input_path.resolve())
    output_str = str(output_path.resolve())
    
    if sys.platform == "win32":
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        word = None
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(input_str)
            doc.SaveAs(output_str, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
            return output_path
        finally:
            if word:
                word.Quit()
            pythoncom.CoUninitialize()
    else:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", input_str, "--outdir", str(output_path.parent)], check=True)
        return output_path

def powerpoint_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Converts PPTX / PPT to PDF."""
    input_str = str(input_path.resolve())
    output_str = str(output_path.resolve())
    
    if sys.platform == "win32":
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        ppt = None
        try:
            ppt = win32com.client.Dispatch("Powerpoint.Application")
            deck = ppt.Presentations.Open(input_str, WithWindow=False)
            deck.SaveAs(output_str, 32)  # 32 = ppSaveAsPDF
            deck.Close()
            return output_path
        finally:
            if ppt:
                ppt.Quit()
            pythoncom.CoUninitialize()
    else:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", input_str, "--outdir", str(output_path.parent)], check=True)
        return output_path

def excel_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Converts XLSX / XLS to PDF."""
    input_str = str(input_path.resolve())
    output_str = str(output_path.resolve())
    
    if sys.platform == "win32":
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        excel = None
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            wb = excel.Workbooks.Open(input_str)
            wb.ExportAsFixedFormat(0, output_str)  # 0 = xlTypePDF
            wb.Close(False)
            return output_path
        finally:
            if excel:
                excel.Quit()
            pythoncom.CoUninitialize()
    else:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", input_str, "--outdir", str(output_path.parent)], check=True)
        return output_path
