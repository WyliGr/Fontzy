# Fontzy

Self-hosted font serving system that replicates the convenience of Google Fonts for fonts you own and host yourself.

## What it does

1. **Upload** your OTF or TTF font files via the web UI or API
2. **Convert** them automatically to WOFF2 (compressed web format) with Latin subsetting
3. **Host** the converted files on your own server
4. **Serve** `@font-face` CSS on demand via a simple URL

## Quick Start

### With Docker

```bash
docker compose up --build
```

Then open http://localhost:8000

### With Python (local development)

Requires Python 3.12+.

```bash
# Install dependencies
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with uv directly:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Upload fonts

Via the web UI at `/`, or via API:

```bash
curl -X POST -F "files=@YourFont.ttf" http://localhost:8000/api/upload
```

### Use in your website

```css
@import url('http://your-server.com/api/font?family=your-font');

body {
  font-family: 'your-font', sans-serif;
}
```

### Request specific weights or styles

```css
@import url('http://your-server.com/api/font?family=your-font&weight=400,700');
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI — browse and upload fonts |
| `/api/font` | GET | Serve `@font-face` CSS for a family |
| `/api/upload` | POST | Upload OTF/TTF files |
| `/api/families` | GET | List all font families |
| `/api/font/{family}` | DELETE | Delete a font family |
| `/fonts/{family}/{file}` | GET | Serve WOFF2 font files (cached for 1 year) |

## Architecture

- **FastAPI** — API server
- **fonttools** + **brotli** — WOFF2 conversion and subsetting
- **Jinja2** — Minimal web UI templates
- **Docker** — Containerized deployment

## Subsetting

By default, fonts are subset to the **Latin** character set, which covers most Western European languages. This significantly reduces file size. Additional subsets (Latin Extended, Cyrillic, Greek) can be added in `app/config.py`.

## Caching

- **CSS responses** — cached for 1 hour
- **Font files** — cached with `immutable` directive for 1 year (content-addressed)

## Notes

- Font licensing is your responsibility. Only upload fonts you have the right to use.
- This is designed for single sites or small deployments. For high-traffic global use, add a CDN in front.
