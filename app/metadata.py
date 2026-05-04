"""Font metadata index management."""

import json
from pathlib import Path
from typing import Any

from app.config import METADATA_FILE, SERVED_DIR


def load_metadata() -> dict[str, Any]:
    if not METADATA_FILE.exists():
        return {"families": {}}
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(data: dict[str, Any]) -> None:
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_font_entry(family: str, weight: int, style: str, path: Path, source_file: str, source_size: int = 0, converted_size: int = 0) -> None:
    """Add a font entry to the metadata index."""
    data = load_metadata()
    families = data.setdefault("families", {})
    family_entry = families.setdefault(family, {})
    weights = family_entry.setdefault("weights", {})
    weight_entry = weights.setdefault(str(weight), {})
    weight_entry[style] = {
        "path": str(path.relative_to(SERVED_DIR)),
        "source": source_file,
        "source_size": source_size,
        "converted_size": converted_size,
    }
    save_metadata(data)


def remove_font_family(family: str) -> None:
    data = load_metadata()
    data.get("families", {}).pop(family, None)
    save_metadata(data)


def list_families() -> list[str]:
    data = load_metadata()
    return sorted(data.get("families", {}).keys())


def get_family(family: str) -> dict[str, Any] | None:
    data = load_metadata()
    return data.get("families", {}).get(family)
