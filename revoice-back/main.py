import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

from routes.upload import router as upload_router

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STORAGE = BASE_DIR / "storage"

ORIGINAL_DIR = STORAGE / "original"
EDIT_DIR = STORAGE / "edit"

ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
EDIT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/original", StaticFiles(directory=str(ORIGINAL_DIR)), name="original")
app.mount("/edit", StaticFiles(directory=str(EDIT_DIR)), name="edit")

app.include_router(upload_router)

if __name__ == "__main__":
    import uvicorn

    HOST                = os.getenv("HOST", "127.0.0.1")
    PORT                = int(os.getenv("PORT", 8000))
    AUTO_RELOAD         = os.getenv("AUTO_RELOAD", "false").lower() == "true"
    RELOAD_EXCLUDES     = os.getenv("RELOAD_EXCLUDES", "").split(",")

    uvicorn.run("main:app", host=HOST, port=PORT, reload=AUTO_RELOAD, reload_excludes=RELOAD_EXCLUDES)