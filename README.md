# YouTube Downloader (Standalone Windows Executable)

A self-contained Windows executable for downloading YouTube videos, audio, and playlists with no requirement for external Python or yt-dlp installations.

## Modern Features & Enhancements

- **100% Standalone**: Python, `yt-dlp`, and `Rich` terminal engine are compiled directly into a single `.exe`.
- **Rich Terminal UI**: Beautiful colored panels, spinners during video loading, and formatted video cards.
- **Clipboard Auto-Detection**: Automatically detects any YouTube link copied to your Windows clipboard and lets you press Enter to use it immediately.
- **Video Summary Card**: Displays the video's title, channel name, duration, and view count before you select the resolution.
- **Smooth Live Progress Bar**: Replaces raw text dumps with a modern progress bar showing percentage, downloaded/total MB, transfer speed, and ETA.
- **Smart Logic Order**:
  1. Auto-detects clipboard link or accepts manual URL input.
  2. If a playlist is detected, prompts for range or whole playlist.
  3. Prompts for Mode: **Video (MP4)** or **Audio only (MP3)**.
  4. **Audio Mode**: Instantly skips video quality questions, extracts best audio track, and saves directly to MP3.
  5. **Video Mode**: Fetches available qualities, presents numbered options with **720p (HD)** as default, merges the best audio track, and embeds English subtitles and thumbnail.
  6. Remembers your last chosen download folder across launches.
  7. Starts downloading immediately without extra summary prompts.
- **Audio Completion Chime**: Plays a subtle Windows notification chime when the download finishes.
- **Automatic FFmpeg Integration**: Checks system PATH or automatically downloads a minimal FFmpeg binary on first launch into `%LOCALAPPDATA%\YouTubeDownloader\ffmpeg`.
- **Update Checker**: Type `U` at the link prompt to check GitHub for the latest `yt-dlp` engine releases.
