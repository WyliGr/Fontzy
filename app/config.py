"""Configuration and settings for Fontzy."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INCOMING_DIR = Path(os.environ.get("FONTZY_INCOMING_DIR", BASE_DIR / "fonts" / "incoming"))
SERVED_DIR = Path(os.environ.get("FONTZY_SERVED_DIR", BASE_DIR / "fonts" / "served"))
METADATA_FILE = Path(os.environ.get("FONTZY_METADATA_FILE", BASE_DIR / "font-metadata.json"))
SETTINGS_FILE = Path(os.environ.get("FONTZY_SETTINGS_FILE", BASE_DIR / "fontzy-settings.json"))

# Default subset: Latin + Latin-1 Supplement
LATIN_SUBSET = (
    "U+0000-00FF,"
    "U+0131,"
    "U+0152-0153,"
    "U+02BB-02BC,"
    "U+02C6,"
    "U+02DA,"
    "U+02DC,"
    "U+0304,"
    "U+0308,"
    "U+0329,"
    "U+2000-206F,"
    "U+2074,"
    "U+20AC,"
    "U+2122,"
    "U+2191,"
    "U+2193,"
    "U+2212,"
    "U+2215,"
    "U+FEFF,"
    "U+FFFD"
)

# Subset presets
SUBSETS = {
    "latin": LATIN_SUBSET,
    "latin-ext": LATIN_SUBSET + ",U+0100-024F,U+0259,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF",
    "cyrillic": "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116",
    "greek": "U+0370-03FF",
}

# Allowed file extensions
SUPPORTED_EXTENSIONS = {".otf", ".ttf"}
