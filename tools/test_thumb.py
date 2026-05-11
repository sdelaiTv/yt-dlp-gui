"""Standalone smoke test: download a YouTube thumbnail through proxy if configured.

Reads proxy from ~/.yt_dlp_gui_settings.json the same way the GUI does.
"""
import io
import json
import sys
import urllib.request
from pathlib import Path

settings = Path.home() / ".yt_dlp_gui_settings.json"
proxy = ""
if settings.exists():
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
        if data.get("proxy_enabled") and data.get("proxy_address"):
            proxy = data["proxy_address"]
            if "://" not in proxy:
                proxy = "http://" + proxy
    except (OSError, json.JSONDecodeError):
        pass

print("proxy:", proxy or "(none)")

url = sys.argv[1] if len(sys.argv) > 1 else "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
print("url:", url)

handlers = []
if proxy:
    handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
else:
    handlers.append(urllib.request.ProxyHandler())
opener = urllib.request.build_opener(*handlers)
req = urllib.request.Request(
    url,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
    },
)
try:
    with opener.open(req, timeout=15) as resp:
        raw = resp.read()
    print("got bytes:", len(raw))
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(raw))
        print("image:", img.size, img.mode, img.format)
    except Exception as exc:  # noqa: BLE001
        print("pil decode failed:", repr(exc))
except Exception as exc:  # noqa: BLE001
    print("download failed:", repr(exc))
