# YouTube Downloader

[![Release](https://img.shields.io/github/v/release/dhruvdankhara/youtube-downloader)](https://github.com/dhruvdankhara/youtube-downloader/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

A modern, fast CLI application and standalone Windows executable for downloading YouTube videos, playlists, and audio tracks with Rich terminal styling, clipboard detection, and automatic FFmpeg management.

---

## Features

- **Rich Terminal Interface**: Built with `rich` for colored status panels, loading spinners, and video summary cards.
- **Live Progress Tracking**: Displays download percentage, speed, total file size, and estimated time remaining (ETA).
- **Clipboard Detection**: Automatically detects YouTube URLs copied to your clipboard—press Enter to download immediately.
- **Video & Audio Modes**:
  - **Video (MP4)**: Choose custom resolutions (1080p, 720p, 480p, 360p) with merged audio and embedded thumbnails.
  - **Audio (MP3)**: Fast extraction directly to high-quality MP3 format.
- **Playlist Support**: Download entire playlists or select custom index ranges.
- **Settings Persistence**: Remembers your preferred download folder across sessions.
- **Automatic FFmpeg Setup**: Automatically downloads and configures FFmpeg in `%LOCALAPPDATA%\YouTubeDownloader\ffmpeg` if not found in your system PATH.
- **Engine Update Checker**: Type `U` at the link prompt to check for the latest `yt-dlp` releases.
- **Batch Script Fallback**: Includes `download.bat` for quick lightweight downloads via command prompt.

---

## Installation & Usage

### Option 1: Standalone Windows Executable (No Python Required)

1. Download `YouTubeDownloader.exe` directly from the [Latest GitHub Release](https://github.com/dhruvdankhara/youtube-downloader/releases/latest).
2. Double-click `YouTubeDownloader.exe` to run.

---

### Option 2: Run from Source (Python)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhruvdankhara/youtube-downloader.git
   cd youtube-downloader
   ```

2. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

---

### Option 3: Build the Standalone Windows Executable Locally

To compile `app.py` into a single standalone `.exe` file using PyInstaller:

```bash
pyinstaller YouTubeDownloader.spec
```

The compiled binary will be placed inside the `dist/` directory:
```
dist/YouTubeDownloader.exe
```

---

### Option 4: Quick Batch Script

You can also run `download.bat` directly in Windows Command Prompt if you have `yt-dlp` installed in your PATH.

---

## Configuration & Cache Paths

The application stores settings and auxiliary tools under the user application directory:
- **Settings**: `%LOCALAPPDATA%\YouTubeDownloader\settings.json`
- **FFmpeg Binary**: `%LOCALAPPDATA%\YouTubeDownloader\ffmpeg\`

---

## Contributing

Contributions, issues, and feature requests are welcome!
Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on opening issues and submitting pull requests.

---

## Disclaimer

This project is created for educational and personal archival purposes. Please respect YouTube's Terms of Service and only download content that you own or have explicit permission/rights to download.

---

## License

This project is licensed under the [MIT License](LICENSE).
