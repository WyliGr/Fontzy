import subprocess, time, urllib.request, sys

proc = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd='/home/will/Documents/Will/Fontzy'
)
time.sleep(3)

req = urllib.request.Request('http://127.0.0.1:8000/')
try:
    with urllib.request.urlopen(req) as resp:
        print('OK:', resp.status)
except urllib.error.HTTPError as e:
    print('Error:', e.code)

proc.terminate()
stdout, stderr = proc.communicate(timeout=5)
print('STDERR:', stderr.decode())
