from pathlib import Path
import pymupdf as fitz
from PIL import Image
import io

def compress_pdf(file_path: Path, output_path: Path, level: str = "medium") -> Path:
    """
    Compresses PDF by cleaning unused resources, deflating streams,
    and optimizing embedded images.
    """
    doc = fitz.open(file_path)
    try:
        if level == "high":
            img_quality = 65
        elif level == "low":
            img_quality = 85
        else:  # medium
            img_quality = 75

        for i in range(len(doc)):
            page = doc[i]
            image_list = page.get_images(full=True)
            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image.get("image")
                image_ext = base_image.get("ext", "").lower()
                
                if image_bytes and image_ext in ("jpeg", "jpg", "png"):
                    try:
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        if pil_img.mode in ("RGBA", "P"):
                            pil_img = pil_img.convert("RGB")
                            
                        out_buffer = io.BytesIO()
                        pil_img.save(out_buffer, format="JPEG", quality=img_quality, optimize=True)
                        new_bytes = out_buffer.getvalue()
                        
                        if len(new_bytes) < len(image_bytes):
                            doc.update_stream(xref, new_bytes)
                    except Exception:
                        pass

        doc.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True
        )
        return output_path
    finally:
        doc.close()

def repair_pdf(file_path: Path, output_path: Path) -> Path:
    """Reconstructs cross-reference (xref) tables and cleans broken stream structures."""
    doc = fitz.open(file_path)
    try:
        doc.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True
        )
        return output_path
    finally:
        doc.close()
