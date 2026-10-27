import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from PIL import Image
import pymupdf as fitz
from pdf2docx import Converter

def _run_libreoffice_convert(input_path: Path, output_path: Path) -> Path:
    """Converts Office documents (DOCX, PPTX, XLSX) to PDF using LibreOffice."""
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice_bin:
        for candidate in [
            "/usr/bin/soffice",
            "/usr/bin/libreoffice",
            "/usr/lib/libreoffice/program/soffice",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        ]:
            if os.path.exists(candidate):
                soffice_bin = candidate
                break

    if not soffice_bin:
        raise RuntimeError(
            "LibreOffice (soffice) bulunamadı. "
            "Sunucu ortamında LibreOffice paketlerinin kurulu olduğundan emin olun."
        )

    parent_dir = output_path.parent.resolve()
    # Isolate user profile to avoid lock conflicts during concurrent conversions
    user_profile = f"file:///tmp/lo_profile_{os.getpid()}_{uuid.uuid4().hex[:6]}"

    cmd = [
        soffice_bin,
        "--headless",
        f"-env:UserInstallation={user_profile}",
        "--convert-to", "pdf",
        str(input_path.resolve()),
        "--outdir", str(parent_dir)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"LibreOffice dönüştürme hatası (çıkış kodu {result.returncode}): {err}")

    # LibreOffice automatically names the output <stem>.pdf in parent_dir
    expected_output = output_path.parent / f"{input_path.stem}.pdf"
    if expected_output.exists():
        if expected_output.resolve() != output_path.resolve():
            if output_path.exists():
                output_path.unlink()
            shutil.move(str(expected_output), str(output_path))
        return output_path

    if output_path.exists():
        return output_path

    # Fallback: search for any freshly generated PDF in the directory
    candidates = [f for f in output_path.parent.glob("*.pdf") if f.resolve() != input_path.resolve()]
    if candidates:
        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if candidates[0].resolve() != output_path.resolve():
            if output_path.exists():
                output_path.unlink()
            shutil.move(str(candidates[0]), str(output_path))
        return output_path

    raise FileNotFoundError(f"Dönüştürülen PDF dosyası oluşturulamadı: {output_path.name}")

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
        try:
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
        except Exception:
            return _run_libreoffice_convert(input_path, output_path)
    else:
        return _run_libreoffice_convert(input_path, output_path)

def powerpoint_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Converts PPTX / PPT to PDF."""
    input_str = str(input_path.resolve())
    output_str = str(output_path.resolve())
    
    if sys.platform == "win32":
        try:
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
        except Exception:
            return _run_libreoffice_convert(input_path, output_path)
    else:
        return _run_libreoffice_convert(input_path, output_path)

def excel_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Converts XLSX / XLS to PDF."""
    input_str = str(input_path.resolve())
    output_str = str(output_path.resolve())
    
    if sys.platform == "win32":
        try:
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
        except Exception:
            return _run_libreoffice_convert(input_path, output_path)
    else:
        return _run_libreoffice_convert(input_path, output_path)
