import urllib.request
import re

# Fetch dashboard
resp = urllib.request.urlopen('http://localhost:8000/')
html = resp.read().decode()

# Find all font preload links
preload_links = re.findall(r'href="([^"]*api/font[^"]*)"', html)
print("Font CSS links found:", preload_links)

# Check if font CSS loads
for url in preload_links:
    try:
        css_resp = urllib.request.urlopen(url)
        css = css_resp.read().decode()
        print(f"\nCSS from {url}:")
        print(css[:200])
    except Exception as e:
        print(f"\nError loading {url}: {e}")

# Find font-family declarations in HTML
families = re.findall(r"font-family: '([^']+)'", html)
print(f"\nFont families in HTML: {set(families)}")

# Find the actual hinato card
if 'hinato' in html:
    idx = html.find('hinato')
    print(f"\nHinato card snippet:")
    print(html[idx-100:idx+200])
