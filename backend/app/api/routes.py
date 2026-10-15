import json
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.config import create_job_workspace
from app.utils.file_manager import create_zip_archive, sanitize_filename, save_upload_file
from app.core.organizer import merge_pdfs, split_pdf, organize_and_rotate_pages, remove_pages
from app.core.converter import (
    images_to_pdf,
    pdf_to_images,
    pdf_to_docx_file,
    pdf_to_markdown_or_text,
    word_to_pdf,
    powerpoint_to_pdf,
    excel_to_pdf
)
from app.core.optimizer import compress_pdf, repair_pdf
from app.core.security import protect_pdf, unlock_pdf
from app.core.editor import add_watermark_text, add_page_numbers, redact_text_occurrences
from app.core.inspector import inspect_pdf, render_page_thumbnail
from app.core.telemetry import track_operation, get_telemetry_summary

router = APIRouter(prefix="/api")

TOOLS_CATALOG = [
    {
        "id": "merge",
        "title": "PDF Birleştir",
        "description": "Birden çok PDF dosyasını dilediğiniz sırada tek bir belgede birleştirin.",
        "category": "organize",
        "icon": "combine",
        "multiple_files": True,
        "accept": ".pdf"
    },
    {
        "id": "split",
        "title": "PDF Böl",
        "description": "Sayfa aralıklarını belirterek PDF'i parçalara veya tek tek sayfalara ayırın.",
        "category": "organize",
        "icon": "split",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "organize",
        "title": "Sayfaları Sırala & Döndür",
        "description": "Sayfaları görsel olarak sürükleyip sıralayın, döndürün veya istemediklerinizi silin.",
        "category": "organize",
        "icon": "layout-grid",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "compress",
        "title": "PDF Sıkıştır",
        "description": "Belge kalitesini koruyarak dosya boyutunu en aza indirin.",
        "category": "optimize",
        "icon": "minimize-2",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "word-to-pdf",
        "title": "Word'den PDF'e",
        "description": "DOCX ve DOC Word belgelerinizi orijinal düzeniyle PDF'e dönüştürün.",
        "category": "convert",
        "icon": "file-text",
        "multiple_files": False,
        "accept": ".docx,.doc"
    },
    {
        "id": "ppt-to-pdf",
        "title": "PowerPoint'ten PDF'e",
        "description": "PPTX ve PPT slayt sunumlarınızı yüksek çözünürlüklü PDF'e çevirin.",
        "category": "convert",
        "icon": "presentation",
        "multiple_files": False,
        "accept": ".pptx,.ppt"
    },
    {
        "id": "excel-to-pdf",
        "title": "Excel'den PDF'e",
        "description": "XLSX ve XLS tablolarınızı nizami sayfa sınırlarıyla PDF yapın.",
        "category": "convert",
        "icon": "table",
        "multiple_files": False,
        "accept": ".xlsx,.xls"
    },
    {
        "id": "pdf-to-word",
        "title": "PDF'ten Word'e",
        "description": "PDF belgelerinizi düzenlenebilir DOCX formatına dönüştürün.",
        "category": "convert",
        "icon": "file-text",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "images-to-pdf",
        "title": "Görselden PDF'e",
        "description": "JPG, PNG, WebP görsellerini tek bir PDF belgesine dönüştürün.",
        "category": "convert",
        "icon": "image",
        "multiple_files": True,
        "accept": "image/*"
    },
    {
        "id": "pdf-to-images",
        "title": "PDF'ten Görsele",
        "description": "PDF'in her sayfasını yüksek çözünürlüklü PNG/JPG resimlere dönüştürün.",
        "category": "convert",
        "icon": "images",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "pdf-to-text",
        "title": "PDF'ten Metne / MD",
        "description": "Belgedeki tüm metinleri biçimlendirilmiş Markdown veya TXT olarak çıkarın.",
        "category": "convert",
        "icon": "code",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "protect",
        "title": "PDF Şifrele",
        "description": "Belgenizi güçlü AES-256 şifreleme ile koruma altına alın.",
        "category": "security",
        "icon": "lock",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "unlock",
        "title": "Şifre Kaldır",
        "description": "Şifresini bildiğiniz PDF'lerin korumasını kalıcı olarak kaldırın.",
        "category": "security",
        "icon": "unlock",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "watermark",
        "title": "Filigran Ekle",
        "description": "Belge sayfalarına özel metin veya mühür filigranı yerleştirin.",
        "category": "organize",
        "icon": "stamp",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "page-numbers",
        "title": "Sayfa Numarası Ekle",
        "description": "İstediğiniz konumda ve biçimde sayfa numaraları basın.",
        "category": "organize",
        "icon": "hash",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "redact",
        "title": "Hassas Bilgi Sansürle",
        "description": "TC Kimlik, telefon, ad soyad gibi terimleri kalıcı olarak PDF'ten kazıyın.",
        "category": "security",
        "icon": "eye-off",
        "multiple_files": False,
        "accept": ".pdf"
    },
    {
        "id": "repair",
        "title": "PDF Onar",
        "description": "Bozuk veya hasarlı PDF belgelerinin indekslerini ve yapısını tamir edin.",
        "category": "optimize",
        "icon": "wrench",
        "multiple_files": False,
        "accept": ".pdf"
    }
]

@router.get("/tools")
def get_tools():
    """Returns the available tools catalog."""
    return {"tools": TOOLS_CATALOG}

@router.get("/stats")
def get_stats():
    """Returns anonymous telemetry usage statistics."""
    return get_telemetry_summary()

@router.post("/inspect")
async def inspect_uploaded_pdf(file: UploadFile = File(...)):
    """Inspects a PDF and returns its structural info and metadata."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    try:
        info = inspect_pdf(input_path)
        info["job_id"] = job_id
        info["filename"] = file.filename
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF incelenemedi: {str(e)}")

@router.get("/thumbnail/{job_id}/{page_index}")
def get_page_thumbnail(job_id: str, page_index: int):
    """Renders a thumbnail image of a specific page from an existing workspace."""
    workspace = create_job_workspace(job_id)
    pdf_files = list(workspace.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="Çalışma alanında PDF bulunamadı")
    
    pdf_path = pdf_files[0]
    thumb_path = workspace / f"thumb_{page_index}.png"
    if not thumb_path.exists():
        try:
            render_page_thumbnail(pdf_path, page_index, thumb_path, max_width=250)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    return FileResponse(thumb_path, media_type="image/png")

@router.post("/merge")
async def handle_merge(files: List[UploadFile] = File(...)):
    """Merges multiple PDF files."""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Birleştirmek için en az 2 PDF yüklemelisiniz.")
        
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    saved_paths = []
    
    for idx, f in enumerate(files):
        target = workspace / f"{idx:03d}_{sanitize_filename(f.filename)}"
        await save_upload_file(f, target)
        saved_paths.append(target)
        
    out_path = workspace / "birlestirilmis_podufu.online.pdf"
    merge_pdfs(saved_paths, out_path)
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/split")
async def handle_split(
    file: UploadFile = File(...),
    ranges: str = Form("all")
):
    """Splits a PDF into separate files or by custom ranges."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    output_files = split_pdf(input_path, ranges, workspace)
    if not output_files:
        raise HTTPException(status_code=400, detail="Belirtilen aralıkta sayfa bulunamadı.")
        
    if len(output_files) == 1:
        return FileResponse(
            output_files[0],
            media_type="application/pdf",
            filename=f"{input_path.stem}_podufu.online.pdf"
        )
    else:
        zip_path = workspace / f"{input_path.stem}_bolumler_podufu.online.zip"
        create_zip_archive(output_files, zip_path)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.name
        )

@router.post("/organize")
async def handle_organize(
    file: UploadFile = File(...),
    instructions: str = Form(...)
):
    """Reorders, rotates, and deletes pages according to user visual arrangement."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    try:
        parsed_instructions = json.loads(instructions)
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz sayfa düzeni verisi.")
        
    out_path = workspace / f"{input_path.stem}_duzenlenmis_podufu.online.pdf"
    organize_and_rotate_pages(input_path, parsed_instructions, out_path)
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/compress")
async def handle_compress(
    file: UploadFile = File(...),
    level: str = Form("medium")
):
    """Compresses a PDF document."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_sikistirilmis_podufu.online.pdf"
    compress_pdf(input_path, out_path, level=level)
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/word-to-pdf")
async def handle_word_to_pdf(file: UploadFile = File(...)):
    """Converts Word (DOCX/DOC) to PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_podufu.online.pdf"
    try:
        word_to_pdf(input_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word dönüştürme hatası: {str(e)}")
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/ppt-to-pdf")
async def handle_ppt_to_pdf(file: UploadFile = File(...)):
    """Converts PowerPoint (PPTX/PPT) to PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_podufu.online.pdf"
    try:
        powerpoint_to_pdf(input_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PowerPoint dönüştürme hatası: {str(e)}")
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/excel-to-pdf")
async def handle_excel_to_pdf(file: UploadFile = File(...)):
    """Converts Excel (XLSX/XLS) to PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_podufu.online.pdf"
    try:
        excel_to_pdf(input_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel dönüştürme hatası: {str(e)}")
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/images-to-pdf")
async def handle_images_to_pdf(files: List[UploadFile] = File(...)):
    """Converts uploaded images into a PDF."""
    if not files:
        raise HTTPException(status_code=400, detail="En az bir görsel yüklemelisiniz.")
        
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    saved_images = []
    
    for idx, f in enumerate(files):
        target = workspace / f"{idx:03d}_{sanitize_filename(f.filename)}"
        await save_upload_file(f, target)
        saved_images.append(target)
        
    out_path = workspace / "gorseller_podufu.online.pdf"
    images_to_pdf(saved_images, out_path)
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/pdf-to-images")
async def handle_pdf_to_images(
    file: UploadFile = File(...),
    dpi: int = Form(200),
    img_format: str = Form("png")
):
    """Converts PDF pages into image files, returned as a ZIP."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    images = pdf_to_images(input_path, workspace, dpi=dpi, img_format=img_format)
    zip_path = workspace / f"{input_path.stem}_gorseller_podufu.online.zip"
    create_zip_archive(images, zip_path)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_path.name
    )

@router.post("/pdf-to-word")
async def handle_pdf_to_word(file: UploadFile = File(...)):
    """Converts PDF to editable Word (.docx)."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_podufu.online.docx"
    try:
        pdf_to_docx_file(input_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word dönüştürme hatası: {str(e)}")
        
    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=out_path.name
    )

@router.post("/pdf-to-text")
async def handle_pdf_to_text(file: UploadFile = File(...)):
    """Extracts text / markdown from PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_metin_podufu.online.md"
    pdf_to_markdown_or_text(input_path, out_path)
    
    return FileResponse(
        out_path,
        media_type="text/markdown",
        filename=out_path.name
    )

@router.post("/protect")
async def handle_protect(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    """Protects PDF with password encryption."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_sifreli_podufu.online.pdf"
    try:
        protect_pdf(input_path, out_path, user_password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/unlock")
async def handle_unlock(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    """Unlocks a password-protected PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_kilitsiz_podufu.online.pdf"
    try:
        unlock_pdf(input_path, out_path, password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/watermark")
async def handle_watermark(
    file: UploadFile = File(...),
    text: str = Form("GİZLİ / KOPYALANAMAZ"),
    opacity: float = Form(0.25),
    rotation: int = Form(45),
    color: str = Form("#FF0000"),
    font_size: int = Form(40)
):
    """Adds a text watermark across all pages."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_filigranli_podufu.online.pdf"
    add_watermark_text(
        input_path,
        out_path,
        text=text,
        opacity=opacity,
        rotation=rotation,
        color_hex=color,
        font_size=font_size
    )
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/page-numbers")
async def handle_page_numbers(
    file: UploadFile = File(...),
    position: str = Form("bottom-center"),
    pattern: str = Form("Sayfa {n} / {total}")
):
    """Adds page numbers to PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_numarali_podufu.online.pdf"
    add_page_numbers(input_path, out_path, position=position, format_pattern=pattern)
    
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )

@router.post("/redact")
async def handle_redact(
    file: UploadFile = File(...),
    search_term: str = Form(...)
):
    """Permanently redacts sensitive text occurrences."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_sansurlu_podufu.online.pdf"
    try:
        _, count = redact_text_occurrences(input_path, out_path, search_term=search_term)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name,
        headers={"X-Redacted-Count": str(count)}
    )

@router.post("/repair")
async def handle_repair(file: UploadFile = File(...)):
    """Repairs corrupt or malformed PDF."""
    job_id = uuid.uuid4().hex
    workspace = create_job_workspace(job_id)
    input_path = workspace / sanitize_filename(file.filename)
    await save_upload_file(file, input_path)
    
    out_path = workspace / f"{input_path.stem}_onarilmis_podufu.online.pdf"
    try:
        repair_pdf(input_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF onarılamadı: {str(e)}")
        
    return FileResponse(
        out_path,
        media_type="application/pdf",
        filename=out_path.name
    )
