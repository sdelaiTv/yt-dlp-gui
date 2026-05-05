# Build Portable EXE (Windows, flash drive)

Goal: one GUI EXE that works on another PC without Python/ffmpeg installation.

## 1) Create venv and install build tool

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip pyinstaller
```

## 2) Prepare runtime files to bundle

Create a local folder structure:

```text
portable-runtime/
  yt-dlp.exe
  ffmpeg/
    ffmpeg.exe
    ffprobe.exe
```

Recommended sources:
- `yt-dlp.exe`: latest release from [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases)
- `ffmpeg.exe` + `ffprobe.exe`: static build from [FFmpeg builds](https://github.com/GyanD/codexffmpeg/releases)

## 3) Build one-file GUI with bundled binaries

Run from repository root:

```powershell
pyinstaller --name yt-dlp-gui --onefile --windowed `
  --add-binary "portable-runtime\yt-dlp.exe;." `
  --add-binary "portable-runtime\ffmpeg\ffmpeg.exe;ffmpeg" `
  --add-binary "portable-runtime\ffmpeg\ffprobe.exe;ffmpeg" `
  --add-data "assets\logo-square.svg;assets" `
  yt_dlp_gui.py
```

Output:
- `dist\yt-dlp-gui.exe`

Bundled assets include:
- `assets/logo-square.svg`

## 4) Verify portable behavior

Before copying to flash drive, test on your PC after temporarily hiding system `ffmpeg` from `PATH`.
App should still work because it resolves:
1. bundled `ffmpeg/ffprobe`
2. bundled `yt-dlp.exe`
3. only then system-level fallbacks

## 5) Distribute

Copy only `dist\yt-dlp-gui.exe` to flash drive and run on target PC.

If SmartScreen warns, sign the executable with a code-signing certificate.
