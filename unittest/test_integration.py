import subprocess, time, urllib.request, json, os

def run_test():
    proc = subprocess.Popen(
        ['python', '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd='/home/will/Documents/Will/Fontzy'
    )
    time.sleep(3)

    try:
        print("=== Fontzy Integration Test ===\n")

        # 1. Test upload
        print("1. Upload font via API")
        boundary = '----Boundary123'
        with open('fonts/incoming/AdwaitaSans-Regular.ttf', 'rb') as f:
            file_data = f.read()
        body = f'--{boundary}\r\n'.encode()
        body += b'Content-Disposition: form-data; name="files"; filename="AdwaitaSans-Regular.ttf"\r\n'
        body += b'Content-Type: application/octet-stream\r\n\r\n'
        body += file_data
        body += f'\r\n--{boundary}--\r\n'.encode()

        req = urllib.request.Request('http://127.0.0.1:8000/api/upload', data=body, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            assert data['results'][0]['status'] == 'converted'
            print("   PASS: Font converted\n")

        # 2. List families
        print("2. List families")
        with urllib.request.urlopen('http://127.0.0.1:8000/api/families') as resp:
            data = json.loads(resp.read().decode())
            assert 'adwaita-sans' in data['families']
            print("   PASS: Family listed\n")

        # 3. Get CSS
        print("3. Get CSS")
        with urllib.request.urlopen('http://127.0.0.1:8000/api/font?family=adwaita-sans') as resp:
            css = resp.read().decode()
            assert 'font-family' in css
            assert 'woff2' in css
            print("   PASS: CSS generated\n")
            print("   CSS preview:")
            for line in css.split('\n')[:6]:
                print(f"      {line}")
            print()

        # 4. Get font file
        print("4. Get font file")
        req = urllib.request.Request('http://127.0.0.1:8000/fonts/adwaita-sans/400-normal.woff2')
        with urllib.request.urlopen(req) as resp:
            font_data = resp.read()
            assert len(font_data) > 1000
            cc = resp.headers.get('Cache-Control')
            assert 'immutable' in cc
            print(f"   PASS: Font file served ({len(font_data)} bytes, Cache-Control: {cc})\n")

        # 5. UI pages
        print("5. UI pages")
        for url in ['http://127.0.0.1:8000/', 'http://127.0.0.1:8000/font/adwaita-sans']:
            with urllib.request.urlopen(url) as resp:
                html = resp.read().decode()
                assert resp.status == 200
                assert '<html' in html.lower()
                print(f"   PASS: {url} renders HTML\n")

        # 6. Delete font
        print("6. Delete font family")
        req = urllib.request.Request('http://127.0.0.1:8000/api/font/adwaita-sans', method='DELETE')
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            assert data['status'] == 'deleted'
            print("   PASS: Font deleted\n")

        # Verify deletion
        print("7. Verify deletion")
        with urllib.request.urlopen('http://127.0.0.1:8000/api/families') as resp:
            data = json.loads(resp.read().decode())
            assert 'adwaita-sans' not in data['families']
            print("   PASS: Family no longer listed\n")

        print("=== All tests passed! ===")

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        proc.terminate()
        proc.wait()

if __name__ == '__main__':
    run_test()
