"""Web UI routes for Fontzy."""

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
import shutil

from jinja2 import Environment, FileSystemLoader

from app.converter import convert_font
from app.metadata import list_families, get_family
from app.config import INCOMING_DIR

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _render(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    families = []
    for name in list_families():
        fam = get_family(name)
        if fam:
            weights = fam.get("weights", {})
            all_styles = set()
            for w, styles in weights.items():
                for s in styles.keys():
                    all_styles.add(s)
            families.append({
                "name": name,
                "weights": sorted([int(w) for w in weights.keys()]),
                "styles": sorted(all_styles),
            })
    html = _render("index.html", request=request, families=families)
    return HTMLResponse(content=html)


@router.get("/font/{family}", response_class=HTMLResponse)
async def font_detail(request: Request, family: str):
    fam = get_family(family)
    if not fam:
        return RedirectResponse(url="/")
    weights = fam.get("weights", {})
    css_url = f"/api/font?family={family}"
    html = _render("detail.html", request=request, family=family, weights=weights, css_url=css_url)
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
