"""FastAPI application entry point."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import SERVED_DIR, INCOMING_DIR, METADATA_FILE, SETTINGS_FILE
from app.router_api import router as api_router
from app.router_ui import router as ui_router

# Ensure directories exist at startup
SERVED_DIR.mkdir(parents=True, exist_ok=True)
INCOMING_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Fontzy", description="Self-hosted font serving system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ui_router)

# Serve static assets (favicon, logo)
ASSETS_DIR = Path(__file__).parent / "assets"
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Serve converted font files with long-term caching
static_app = StaticFiles(directory=str(SERVED_DIR))

@app.get("/fonts/{family}/{file_name}")
async def serve_font(family: str, file_name: str):
    file_path = SERVED_DIR / family / file_name
    if not file_path.is_file():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Font file not found")
    return FileResponse(
        str(file_path),
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Access-Control-Allow-Origin": "*",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
