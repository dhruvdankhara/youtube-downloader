# YouTube Downloader (Standalone Windows Executable)

A self-contained Windows executable for downloading YouTube videos, audio, and playlists with no requirement for external Python or yt-dlp installations.

## Features

- **100% Standalone**: Python and `yt-dlp` are compiled directly into a single `.exe`. No external packages or runtimes required.
- **Smart Logic Order**:
  1. Prompts for video or playlist link.
  2. If a playlist is detected, prompts for range or whole playlist.
  3. Prompts for Mode: **Video (MP4)** or **Audio only (MP3)**.
  4. **Audio Mode**: Instantly skips video quality questions, extracts best audio track, and saves directly to MP3.
  5. **Video Mode**: Fetches available qualities, presents numbered options with **720p (HD)** as default, merges the best audio track, and embeds English subtitles and thumbnail.
  6. Prompts for destination folder (defaults to Windows `Downloads`, press `B` for folder picker dialog).
  7. Starts downloading immediately without extra summary prompts.
- **Automatic FFmpeg Integration**: Checks system PATH or automatically downloads a minimal FFmpeg binary on first launch into `%LOCALAPPDATA%\YouTubeDownloader\ffmpeg` for high-resolution video merging and MP3 conversion.
- **Update Checker**: Type `U` at the link prompt to check GitHub for the latest `yt-dlp` engine releases.
- **Clean Exit**: Press any key to close the console when the download finishes.

## How to Use

1. Double-click `YouTubeDownloader.exe` to run.
2. Paste any YouTube video or playlist URL.
3. Select Video (1) or Audio (2).
4. If Video, select desired quality (or press Enter for 720p).
5. Press Enter to download to `Downloads`, or press `B` to choose a custom folder.
