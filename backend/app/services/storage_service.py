import os
import uuid
import aiofiles
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.file import StoredFile

UPLOAD_DIR = "uploads"

async def save_upload(db: Session, file: UploadFile) -> StoredFile:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, safe_name)

    size = 0
    async with aiofiles.open(path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            await f.write(chunk)

    record = StoredFile(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        path=path,
        size_bytes=size,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
