"""Generate @font-face CSS on demand."""

from app.config import SERVED_DIR
from app.metadata import get_family


def generate_css(family: str, weights: list[int] | None = None, style: str | None = None, base_url: str = "") -> str:
    """Generate @font-face CSS rules for requested family."""
    family_data = get_family(family)
    if not family_data:
        return ""

    lines: list[str] = []
    available_weights = family_data.get("weights", {})

    for w_str, styles in available_weights.items():
        w = int(w_str)
        if weights is not None and w not in weights:
            continue
        for s, info in styles.items():
            if style is not None and s != style:
                continue
            path = info["path"]
            url = f"{base_url.rstrip('/')}/{path}"
            lines.append(
                f"@font-face {{\n"
                f"  font-family: '{family}';\n"
                f"  font-style: {s};\n"
                f"  font-weight: {w};\n"
                f"  font-display: swap;\n"
                f"  src: url('{url}') format('woff2');\n"
                f"}}"
            )

    return "\n\n".join(lines)
