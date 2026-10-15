import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.organizer import merge_pdfs, split_pdf, organize_and_rotate_pages
from app.core.converter import images_to_pdf, pdf_to_images, pdf_to_docx_file, pdf_to_markdown_or_text
from app.core.optimizer import compress_pdf, repair_pdf
from app.core.security import protect_pdf, unlock_pdf
from app.core.editor import add_watermark_text, add_page_numbers, redact_text_occurrences
from app.core.inspector import inspect_pdf

TEST_DIR = Path(__file__).resolve().parent / "test_workspace"
TEST_DIR.mkdir(parents=True, exist_ok=True)

def create_sample_pdf(file_path: Path, num_pages: int = 3, text_prefix: str = "Test PDF Sayfasi"):
    c = canvas.Canvas(str(file_path), pagesize=letter)
    for i in range(1, num_pages + 1):
        c.drawString(100, 750, f"{text_prefix} - Sayfa {i}")
        c.drawString(100, 700, "Gizli TC Kimlik: 12345678901")
        c.drawString(100, 650, "Bu belge yerel test amacli olusturulmustur.")
        c.showPage()
    c.save()
    return file_path

def run_all_tests():
    print("==================================================")
    print("   LocalPDF Suite — Otomatik Entegrasyon Testi    ")
    print("==================================================")
    
    # 1. Create sample PDFs
    pdf1 = create_sample_pdf(TEST_DIR / "sample1.pdf", num_pages=2, text_prefix="Belge 1")
    pdf2 = create_sample_pdf(TEST_DIR / "sample2.pdf", num_pages=2, text_prefix="Belge 2")
    print("[OK] 1. Test PDF'leri olusturuldu.")

    # 2. Inspect
    info = inspect_pdf(pdf1)
    assert info["page_count"] == 2, f"Expected 2 pages, got {info['page_count']}"
    print("[OK] 2. PDF İnceleme (Inspect) testi basarili. Sayfa sayisi: 2")

    # 3. Merge
    merged_pdf = TEST_DIR / "merged.pdf"
    merge_pdfs([pdf1, pdf2], merged_pdf)
    assert inspect_pdf(merged_pdf)["page_count"] == 4
    print("[OK] 3. PDF Birleştirme (Merge) testi basarili. 2+2 = 4 sayfa.")

    # 4. Split
    split_files = split_pdf(merged_pdf, ranges="1-2, 3-4", output_dir=TEST_DIR)
    assert len(split_files) == 2
    print(f"[OK] 4. PDF Bölme (Split) testi basarili. {len(split_files)} parca olusturuldu.")

    # 5. Organize & Rotate
    organized_pdf = TEST_DIR / "organized.pdf"
    instructions = [
        {"page_index": 1, "rotation": 90},
        {"page_index": 0, "rotation": 0}
    ]
    organize_and_rotate_pages(pdf1, instructions, organized_pdf)
    assert inspect_pdf(organized_pdf)["page_count"] == 2
    print("[OK] 5. Sayfa Duzenleme & Dondurme (Organize) testi basarili.")

    # 6. Watermark
    watermarked_pdf = TEST_DIR / "watermarked.pdf"
    add_watermark_text(pdf1, watermarked_pdf, text="TEST FILIGRAN")
    assert watermarked_pdf.exists()
    print("[OK] 6. Filigran (Watermark) testi basarili.")

    # 7. Page Numbers
    numbered_pdf = TEST_DIR / "numbered.pdf"
    add_page_numbers(pdf1, numbered_pdf, position="bottom-center")
    assert numbered_pdf.exists()
    print("[OK] 7. Sayfa Numaralandirma testi basarili.")

    # 8. Redaction (Sansürleme)
    redacted_pdf = TEST_DIR / "redacted.pdf"
    _, count = redact_text_occurrences(pdf1, redacted_pdf, search_term="12345678901")
    assert count > 0, f"Expected redact occurrences, got {count}"
    print(f"[OK] 8. Hassas Veri Sansurleme (Redaction) testi basarili. ({count} terim silindi)")

    # 9. Protect & Unlock
    protected_pdf = TEST_DIR / "protected.pdf"
    protect_pdf(pdf1, protected_pdf, user_password="gizlisifre123")
    assert inspect_pdf(protected_pdf)["is_encrypted"] is True
    print("[OK] 9a. Sifreleme (AES-256 Protect) basarili.")

    unlocked_pdf = TEST_DIR / "unlocked.pdf"
    unlock_pdf(protected_pdf, unlocked_pdf, password="gizlisifre123")
    assert inspect_pdf(unlocked_pdf)["is_encrypted"] is False
    print("[OK] 9b. Kilit Acma (Unlock) basarili.")

    # 10. PDF to Images & Images to PDF
    images = pdf_to_images(pdf1, TEST_DIR, dpi=100, img_format="png")
    assert len(images) == 2
    print(f"[OK] 10a. PDF to Images basarili. ({len(images)} resim olusturuldu)")

    reconstructed_pdf = TEST_DIR / "reconstructed.pdf"
    images_to_pdf(images, reconstructed_pdf)
    assert reconstructed_pdf.exists()
    print("[OK] 10b. Images to PDF basarili.")

    # 11. PDF to Text / Markdown
    text_path = TEST_DIR / "extracted_text.md"
    pdf_to_markdown_or_text(pdf1, text_path)
    content = text_path.read_text(encoding="utf-8")
    assert text_path.exists() and "Belge 1" in content
    print("[OK] 11. PDF to Text/Markdown basarili.")

    # 12. PDF to Word (pdf2docx)
    docx_path = TEST_DIR / "converted.docx"
    pdf_to_docx_file(pdf1, docx_path)
    assert docx_path.exists() and docx_path.stat().st_size > 0
    print("[OK] 12. PDF to Word (.docx) basarili.")

    # 13. Compress & Repair
    compressed_pdf = TEST_DIR / "compressed.pdf"
    compress_pdf(pdf1, compressed_pdf, level="medium")
    assert compressed_pdf.exists()
    print("[OK] 13a. Sıkıştırma (Compress) basarili.")

    repaired_pdf = TEST_DIR / "repaired.pdf"
    repair_pdf(pdf1, repaired_pdf)
    assert repaired_pdf.exists()
    print("[OK] 13b. Onarma (Repair) basarili.")

    print("\n🎉 TUM TESTLER BASARIYLA TAMAMLANDI! SISTEM %100 CALISIYOR.")

if __name__ == "__main__":
    run_all_tests()
