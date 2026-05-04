"""Web UI routes for Fontzy."""

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
import shutil

from jinja2 import Environment, FileSystemLoader

from app.converter import convert_font
from app.metadata import list_families, get_family
from app.config import INCOMING_DIR
from app.settings import get_base_url

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _render(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


def _human_size(size_bytes: int) -> str:
    """Convert bytes to human readable string."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _get_base_url(request: Request) -> str:
    """Return configured base URL or fallback to request origin."""
    configured = get_base_url().rstrip("/")
    if configured:
        return configured
    return str(request.base_url).rstrip("/")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    families = []
    total_source = 0
    total_converted = 0
    base_url = _get_base_url(request)
    for name in list_families():
        fam = get_family(name)
        if fam:
            weights = fam.get("weights", {})
            all_styles = set()
            variants = 0
            fam_source = 0
            fam_converted = 0
            for w, styles in weights.items():
                for s, info in styles.items():
                    all_styles.add(s)
                    variants += 1
                    fam_source += info.get("source_size", 0)
                    fam_converted += info.get("converted_size", 0)
            total_source += fam_source
            total_converted += fam_converted
            savings = round((1 - fam_converted / fam_source) * 100) if fam_source > 0 else 0
            families.append({
                "name": name,
                "weights": sorted([int(w) for w in weights.keys()]),
                "styles": sorted(all_styles),
                "variants": variants,
                "source_size": _human_size(fam_source),
                "converted_size": _human_size(fam_converted),
                "savings": savings,
            })
    html = _render(
        "index.html",
        request=request,
        families=families,
        total_families=len(families),
        total_source=_human_size(total_source),
        total_converted=_human_size(total_converted),
        base_url=base_url,
    )
    return HTMLResponse(content=html)


@router.get("/font/{family}", response_class=HTMLResponse)
async def font_detail(request: Request, family: str):
    fam = get_family(family)
    if not fam:
        return RedirectResponse(url="/")
    weights = fam.get("weights", {})
    base_url = _get_base_url(request)
    css_url = f"{base_url}/api/font?family={family}"

    variants = []
    for w_str, styles in weights.items():
        w = int(w_str)
        for s, info in styles.items():
            variants.append({
                "weight": w,
                "style": s,
                "path": info.get("path", ""),
                "source_size": _human_size(info.get("source_size", 0)),
                "converted_size": _human_size(info.get("converted_size", 0)),
            })

    html = _render(
        "detail.html",
        request=request,
        family=family,
        weights=weights,
        variants=variants,
        css_url=css_url,
        base_url=base_url,
    )
    return HTMLResponse(content=html)


@router.post("/upload")
async def ui_upload(files: list[UploadFile] = File(...)):
    for upload in files:
        if not upload.filename:
            continue
        ext = Path(upload.filename).suffix.lower()
        if ext not in {".otf", ".ttf"}:
            continue
        dest = INCOMING_DIR / upload.filename
        INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        out = convert_font(dest)
        if out:
            dest.unlink(missing_ok=True)
    return RedirectResponse(url="/", status_code=303)
