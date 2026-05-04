import subprocess, time, urllib.request

proc = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd='/home/will/Documents/Will/Fontzy'
)
time.sleep(3)

for url in ['http://127.0.0.1:8000/', 'http://127.0.0.1:8000/font/adwaita-sans']:
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode()
            title_start = data.find('<title>') + 7
            title_end = data.find('</title>')
            title = data[title_start:title_end]
            print(f"{url}: status={resp.status}, length={len(data)}, title='{title}'")
    except urllib.error.HTTPError as e:
        print(f"{url}: error={e.code}")

proc.terminate()
proc.wait()
print("Done")
