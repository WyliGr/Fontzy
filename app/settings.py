"""Application settings persistence."""

import json
from pathlib import Path
from typing import Any

from app.config import SETTINGS_FILE


def load_settings() -> dict[str, Any]:
    """Load settings from JSON file."""
    if not SETTINGS_FILE.exists():
        return {"base_url": ""}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data: dict[str, Any]) -> None:
    """Save settings to JSON file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_base_url() -> str:
    """Get configured base URL, guaranteed to end with trailing slash if non-empty."""
    settings = load_settings()
    url = settings.get("base_url", "").strip()
    if url and not url.endswith("/"):
        url += "/"
    return url


def set_base_url(url: str) -> None:
    """Set the base URL."""
    settings = load_settings()
    settings["base_url"] = url.strip().rstrip("/")
    save_settings(settings)
