"""Static file serving routes – must be registered LAST (catch-all)."""
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse
router = APIRouter()
WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"
@router.get("/")
def index():
    f = WEB_DIR / "index.html"
    if f.exists():
        return FileResponse(f)
    return {"app": "aetherswap", "ui": "web/index.html not found"}
@router.get("/{path:path}")
def static_or_index(path: str):
    f = WEB_DIR / path
    if f.is_file():
        return FileResponse(f)
    if (WEB_DIR / "index.html").exists():
        return FileResponse(WEB_DIR / "index.html")
    return {"error": "not found"}
