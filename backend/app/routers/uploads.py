"""File Upload Router for Request Module"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from pathlib import Path

from ..database import get_db
from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Upload configuration
UPLOAD_DIR = Path("uploads/requests")
ALLOWED_EXTENSIONS = {
    'word': ['.doc', '.docx'],
    'excel': (['.xls', '.xlsx']),
    'pdf': ['.pdf'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_type(filename) is not None


@router.post("/item-file")
async def upload_item_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file for a request item (Word/Excel/PDF/Image)"""
    print(f"Received upload request: {file.filename}, content_type={file.content_type}")
    
    # Validate file type
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: Word, Excel, PDF, Images"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum of {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return file info
    return {
        "filename": file.filename,
        "saved_filename": safe_filename,
        "path": str(file_path),
        "type": get_file_type(file.filename),
        "size": len(file_content)
    }


@router.get("/item-file/{filename}")
async def download_item_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Download an uploaded item file"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Extract original filename (remove timestamp prefix)
    # Format: YYYYMMDD_HHMMSS_originalfilename.ext
    try:
        parts = filename.split('_', 2)
        if len(parts) == 3:
            original_filename = parts[2]
        else:
            original_filename = filename
    except:
        original_filename = filename
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type='application/octet-stream'
    )


@router.delete("/item-file/{filename}")
async def delete_item_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded item file"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
