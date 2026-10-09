import urllib.request
import zipfile
import io
import os
import shutil

def download():
    print("Downloading Stockfish 17 for Windows...")
    url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_17/stockfish-windows-x86-64-avx2.zip"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    print(f"Downloaded {len(data)} bytes")

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if name.endswith('.exe'):
                out_path = os.path.join(os.path.dirname(__file__), 'stockfish.exe')
                with z.open(name) as src, open(out_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                print(f"Successfully saved Stockfish executable to: {out_path}")
                return True
    print("Failed to find .exe in zip archive")
    return False

if __name__ == '__main__':
    download()
