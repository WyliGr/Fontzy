"""Font conversion: OTF/TTF parse, subset, WOFF2 export."""

import os
import re
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

from app.config import INCOMING_DIR, SERVED_DIR, SUBSETS, SUPPORTED_EXTENSIONS
from app.metadata import add_font_entry


def _normalize_name(name: str) -> str:
    # Lowercase, replace spaces and underscores with hyphens
    return re.sub(r"[\s_]+", "-", name.strip()).lower()


def _get_font_metadata(font: TTFont) -> tuple[str, int, str]:
    """Extract (family_name, weight, style) from font tables."""
    name_table = font["name"]
    family_name = None
    subfamily_name = None
    weight = 400
    style = "normal"

    for record in name_table.names:
        if record.nameID == 1 and family_name is None:
            family_name = str(record).strip()
        if record.nameID == 2 and subfamily_name is None:
            subfamily_name = str(record).strip()
        if record.nameID == 16 and family_name is None:
            family_name = str(record).strip()
        if record.nameID == 17 and subfamily_name is None:
            subfamily_name = str(record).strip()

    if not family_name:
        family_name = "unknown"
    if not subfamily_name:
        subfamily_name = "Regular"

    subfamily_lower = subfamily_name.lower()
    if "italic" in subfamily_lower:
        style = "italic"

    weight_keywords = {
        "thin": 100, "extra light": 200, "extralight": 200, "light": 300,
        "regular": 400, "normal": 400, "medium": 500,
        "semi bold": 600, "semibold": 600, "bold": 700,
        "extra bold": 800, "extrabold": 800, "black": 900,
    }
    for keyword, w in weight_keywords.items():
        if keyword in subfamily_lower:
            weight = w
            break

    if "OS/2" in font:
        os2_weight = font["OS/2"].usWeightClass
        if 100 <= os2_weight <= 900:
            weight = os2_weight

    family_name = _normalize_name(family_name)
    return family_name, weight, style


def _rename_font(font: TTFont, new_family: str) -> None:
    """Update the font's name table to use the normalized family name."""
    name_table = font["name"]
    for record in name_table.names:
        if record.nameID in (1, 16):
            # Family name
            try:
                record.string = new_family.encode(record.getEncoding())
            except Exception:
                # Fallback: just set as UTF-16-BE (Windows) or UTF-8 (Mac)
                if record.platformID == 1:
                    record.string = new_family.encode("mac_roman")
                elif record.platformID == 3:
                    record.string = new_family.encode("utf_16_be")
                else:
                    record.string = new_family.encode("utf_8")


def _parse_unicodes(subset_str: str) -> list[int]:
    """Parse a subset string like 'U+0000-00FF,U+0131' into a list of ints."""
    codes = []
    for part in subset_str.split(","):
        part = part.strip()
        if not part:
            continue
        if part.startswith("U+") or part.startswith("u+"):
            part = part[2:]
        if "-" in part:
            start, end = part.split("-", 1)
            codes.extend(range(int(start, 16), int(end, 16) + 1))
        else:
            codes.append(int(part, 16))
    return codes


def convert_font(source_path: Path, subset_key: str = "latin") -> Path | None:
    """Convert a single OTF/TTF file to subsetted WOFF2 and index it."""
    if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return None

    try:
        font = TTFont(str(source_path))
    except Exception:
        return None

    family_name, weight, style = _get_font_metadata(font)

    # Rename font family in the file to match the normalized name
    _rename_font(font, family_name)

    # Subset
    subset_codes = _parse_unicodes(SUBSETS.get(subset_key, SUBSETS["latin"]))
    options = Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    options.layout_features = "*"
    options.name_IDs = "*"
    options.notdef_outline = True
    options.ignore_missing_glyphs = True
    options.ignore_missing_unicodes = True
    options.recalc_bounds = True
    options.recalc_timestamp = True
    options.prune_unicode_ranges = True

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=subset_codes)
    subsetter.subset(font)

    # Build output path
    out_dir = SERVED_DIR / family_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{weight}-{style}.woff2"

    font.flavor = "woff2"
    font.save(str(out_file))
    font.close()

    source_size = source_path.stat().st_size if source_path.exists() else 0
    converted_size = out_file.stat().st_size if out_file.exists() else 0
    add_font_entry(family_name, weight, style, out_file, source_path.name, source_size=source_size, converted_size=converted_size)
    return out_file


def scan_and_convert(subset_key: str = "latin") -> list[Path]:
    """Scan incoming directory and convert any new fonts."""
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    SERVED_DIR.mkdir(parents=True, exist_ok=True)

    converted = []
    for ext in SUPPORTED_EXTENSIONS:
        for path in INCOMING_DIR.glob(f"*{ext}"):
            result = convert_font(path, subset_key=subset_key)
            if result:
                converted.append(result)
                os.remove(path)
    return converted
