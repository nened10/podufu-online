from pathlib import Path
from pypdf import PdfReader, PdfWriter

def protect_pdf(file_path: Path, output_path: Path, user_password: str, owner_password: str = None) -> Path:
    """Encrypts a PDF using AES-256 or AES-128 bit encryption."""
    if not user_password:
        raise ValueError("Şifre boş olamaz.")
        
    reader = PdfReader(str(file_path))
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        algorithm="AES-256"
    )
    
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    return output_path

def unlock_pdf(file_path: Path, output_path: Path, password: str) -> Path:
    """Removes encryption from a protected PDF if the password is correct."""
    reader = PdfReader(str(file_path))
    if reader.is_encrypted:
        decrypt_result = reader.decrypt(password)
        if decrypt_result == 0:
            raise ValueError("Hatalı şifre! Belge açılamadı.")
            
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    return output_path
