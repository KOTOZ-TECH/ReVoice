from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid
import aiofiles
import os
from services.audio_processing.service import process_audio 

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DIR = BASE_DIR / "storage" / "original"
ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    file_extension = Path(file.filename).suffix
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}{file_extension}"
    file_path = ORIGINAL_DIR / filename
    file_base_url =  os.getenv("FILE_BASE_URL", "http://api.revoice.kotoz.tech") # Укажите вашу модель
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)

    results = process_audio(str(file_path))

    return {
        "status": "success",
        "uuid": unique_id,
        "urls": {
            "original": f"{file_base_url}/original/{filename}",
            "edit": f"{file_base_url}/edit/{results['edit_url']}",
        },
        "transcriptions": {
            "orig": results["original_text"],
            "edit": results["redacted_text"],
        },
        "red_zones": results["red_zones"],
    }