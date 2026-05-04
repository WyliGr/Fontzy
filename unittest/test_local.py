"""Test script for local font conversion and CSS generation."""

import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from app.converter import convert_font
from app.css_generator import generate_css
from app.metadata import load_metadata

# Clean up previous test data
metadata = Path("font-metadata.json")
if metadata.exists():
    metadata.unlink()
served_dir = Path("fonts/served")
if served_dir.exists():
    for item in served_dir.iterdir():
        if item.is_dir():
            for f in item.iterdir():
                f.unlink()
            item.rmdir()

# Test conversion
source = Path("fonts/incoming/AdwaitaSans-Regular.ttf")
if not source.exists():
    print(f"ERROR: Source font not found at {source}")
    sys.exit(1)

print(f"Converting {source}...")
result = convert_font(source)
print(f"Result: {result}")

# Check metadata
meta = load_metadata()
print(f"Metadata families: {list(meta.get('families', {}).keys())}")

# Test CSS generation
css = generate_css("adwaita-sans")
print(f"\nGenerated CSS:\n{css[:500]}...")

# Test with different base_url
css2 = generate_css("adwaita-sans", base_url="/fonts")
print(f"\nCSS with base_url='/fonts':\n{css2[:500]}...")
