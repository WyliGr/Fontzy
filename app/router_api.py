"""API routes for Fontzy."""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pathlib import Path
import shutil

from app.config import INCOMING_DIR, SERVED_DIR
from app.converter import convert_font
from app.css_generator import generate_css
from app.metadata import remove_font_family, list_families, get_family

router = APIRouter(prefix="/api")


@router.get("/font", response_class=PlainTextResponse)
async def serve_font_css(
    request: Request,
    family: str = Query(..., description="Font family name"),
    weight: str | None = Query(None, description="Comma-separated weights, e.g. 400,700"),
    style: str | None = Query(None, description="Font style, e.g. normal or italic"),
):
    weights = None
    if weight:
        try:
            weights = [int(w.strip()) for w in weight.split(",") if w.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid weight parameter")

    css = generate_css(family, weights=weights, style=style, base_url="/fonts")
    if not css:
        raise HTTPException(status_code=404, detail="Font family not found")

    return PlainTextResponse(
        content=css,
        media_type="text/css",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.post("/upload")
async def upload_fonts(files: list[UploadFile] = File(...)):
    results = []
    for upload in files:
        if not upload.filename:
            continue
        ext = Path(upload.filename).suffix.lower()
        if ext not in {".otf", ".ttf"}:
            results.append({"filename": upload.filename, "status": "skipped", "reason": "Unsupported file type"})
            continue
        dest = INCOMING_DIR / upload.filename
        INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        out = convert_font(dest)
        if out:
            results.append({"filename": upload.filename, "status": "converted", "path": str(out)})
            # Clean up source after conversion
            dest.unlink(missing_ok=True)
        else:
            results.append({"filename": upload.filename, "status": "error", "reason": "Conversion failed"})
    return JSONResponse(content={"results": results})


@router.delete("/font/{family}")
async def delete_font_family(family: str):
    fam = get_family(family)
    if not fam:
        raise HTTPException(status_code=404, detail="Font family not found")

    # Remove served files
    fam_dir = SERVED_DIR / family
    if fam_dir.exists():
        shutil.rmtree(fam_dir)

    remove_font_family(family)
    return JSONResponse(content={"status": "deleted", "family": family})


@router.get("/families")
async def list_font_families():
    return JSONResponse(content={"families": list_families()})
