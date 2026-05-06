# Best Video Downloader (yt-dlp GUI Fork)

Desktop GUI fork of `yt-dlp` for convenient video/audio downloading.

This project wraps the power of `yt-dlp` in a modern interface with presets, logs, templates, and portable Windows build support.

<img width="860" height="800" alt="downloader" src="https://github.com/user-attachments/assets/9da3925f-4063-4e74-85f2-48ded5ac1ca6" />

## About

- This repository is a **fork based on `yt-dlp`** with a custom graphical interface.
- GUI is implemented in Python (`tkinter`) and designed for regular users who do not want to work in CLI.
- The app supports:
  - URL/playlist downloads
  - video and audio modes
  - subtitle options
  - proxy/cookies options
  - filename template presets + custom template
  - Plex/Emby-oriented output layout
  - multilingual UI (RU / EN / 中文)

## Free Use

- This GUI fork is provided **for free use**.
- No paid activation, no subscription.

## Upstream Credits

This project is built on top of the excellent open-source downloader:

- [yt-dlp (upstream project)](https://github.com/yt-dlp/yt-dlp)

## Project Structure

- `yt_dlp_gui.py` — main GUI application
- `portable-runtime/` — runtime binaries bundled into portable EXE
  - `yt-dlp.exe`
  - `ffmpeg/ffmpeg.exe`
  - `ffmpeg/ffprobe.exe`
- `dist/yt-dlp-gui.exe` — built portable GUI executable

## Run From Source

Requirements:

- Python 3.10+ (recommended 3.12)
- Windows (current build scripts and packaging flow are Windows-focused)

Run:

```powershell
python yt_dlp_gui.py
```

## Build Portable EXE

This produces a single `yt-dlp-gui.exe` that can be copied to another PC.

### 1) Install PyInstaller

```powershell
python -m pip install -U pyinstaller
```

### 2) Ensure runtime binaries exist

Required files:

- `portable-runtime/yt-dlp.exe`
- `portable-runtime/ffmpeg/ffmpeg.exe`
- `portable-runtime/ffmpeg/ffprobe.exe`

### 3) Build

```powershell
pyinstaller --name yt-dlp-gui --onefile --windowed --noconfirm `
  --add-binary "portable-runtime/yt-dlp.exe;." `
  --add-binary "portable-runtime/ffmpeg/ffmpeg.exe;ffmpeg" `
  --add-binary "portable-runtime/ffmpeg/ffprobe.exe;ffmpeg" `
  yt_dlp_gui.py
```

Result:

- `dist/yt-dlp-gui.exe`

## How To Use

1. Launch `yt-dlp-gui.exe` (or `python yt_dlp_gui.py`)
2. Paste URL/playlist
3. Choose output folder
4. Select download mode:
   - Video + Audio
   - Audio only
5. (Optional) Configure templates, subtitles, proxy, cookies
6. Click **Start Download**

### Filename Templates

- Built-in presets + custom editable template
- Live preview of resulting output template
- Plex/Emby profile available for per-item folder structure and metadata sidecars

## Notes

- Stop action terminates download process tree on Windows.
- App auto-uses bundled ffmpeg when available.
- Logs are decoded using system encoding for better Windows locale compatibility.


