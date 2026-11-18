import os
import sys
import shutil
import zipfile
import urllib.request
import json
import re
import ctypes
from pathlib import Path

# Enable ANSI escape sequences in Windows console and line buffering
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

if os.name == 'nt':
    os.system('')
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("YT-DLP Advanced Downloader")
    except Exception:
        pass

# Color codes
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

import yt_dlp

def print_banner():
    print(f"{GREEN}=========================================")
    print("       YT-DLP Advanced Downloader")
    print(f"========================================={RESET}\n")

def pause_and_exit(code=0):
    if sys.stdin.isatty():
        print("\nPress any key to exit...")
        try:
            import msvcrt
            msvcrt.getch()
        except Exception:
            try:
                input()
            except Exception:
                pass
    else:
        print("\n[Exiting]")
    sys.exit(code)

def get_default_download_dir():
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        return str(downloads)
    return os.getcwd()

def browse_folder_gui(initial_dir):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        selected = filedialog.askdirectory(initialdir=initial_dir, title="Select Download Folder")
        root.destroy()
        return selected if selected else None
    except Exception as e:
        print(f"{YELLOW}[WARN] Could not open graphical folder picker: {e}{RESET}")
        return None

def check_for_updates():
    print(f"\n{CYAN}[INFO] Checking for yt-dlp updates...{RESET}")
    current_ver = yt_dlp.version.__version__
    print(f"Current version: {current_ver}")
    try:
        req = urllib.request.Request(
            'https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode('utf-8'))
            latest_ver = data.get('tag_name', '').lstrip('v')
            if latest_ver and latest_ver != current_ver:
                print(f"{YELLOW}[UPDATE AVAILABLE] A newer version of yt-dlp ({latest_ver}) is available.{RESET}")
                print(f"Release URL: {data.get('html_url')}")
            else:
                print(f"{GREEN}[OK] You are running the latest yt-dlp engine ({current_ver}).{RESET}")
    except Exception as e:
        print(f"{RED}[WARN] Update check failed: {e}{RESET}")
    print()

def download_progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, (downloaded / total_size) * 100)
        mb_down = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        bar_len = 30
        filled = int(bar_len * percent / 100)
        bar = '=' * filled + '-' * (bar_len - filled)
        sys.stdout.write(f"\r[{bar}] {percent:.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)")
        sys.stdout.flush()

def ensure_ffmpeg():
    # 1. System PATH
    ffmpeg_cmd = shutil.which("ffmpeg")
    ffprobe_cmd = shutil.which("ffprobe")
    if ffmpeg_cmd and ffprobe_cmd:
        return os.path.dirname(ffmpeg_cmd)

    # 2. Local AppData cache folder
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    ffmpeg_dir = os.path.join(local_app_data, "YouTubeDownloader", "ffmpeg")
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        return ffmpeg_dir

    # 3. Application directory
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    app_ffmpeg = os.path.join(base_dir, "ffmpeg")
    if os.path.exists(os.path.join(app_ffmpeg, "ffmpeg.exe")):
        return app_ffmpeg

    # 4. If missing, auto-download
    print(f"{YELLOW}[INFO] FFmpeg was not detected on this system.{RESET}")
    print(f"{YELLOW}[INFO] FFmpeg is required for 1080p+ video merging and MP3 conversion.{RESET}")
    print(f"{GREEN}[INFO] Downloading minimal FFmpeg package (one-time setup)...{RESET}")

    os.makedirs(ffmpeg_dir, exist_ok=True)
    zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")

    urls = [
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ]

    download_success = False
    for url in urls:
        try:
            print(f"Connecting to: {url} ...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response, open(zip_path, 'wb') as out_file:
                total_length = response.headers.get('content-length')
                total_size = int(total_length) if total_length else 0
                block_size = 64 * 1024
                downloaded = 0
                block_num = 0
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    out_file.write(buffer)
                    downloaded += len(buffer)
                    block_num += 1
                    download_progress_hook(block_num, block_size, total_size)
            print("\nDownload complete.")
            download_success = True
            break
        except Exception as e:
            print(f"\n{RED}[WARN] Failed to download from {url}: {e}{RESET}")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass

    if not download_success:
        print(f"{RED}[ERROR] Could not automatically download FFmpeg. Please ensure internet access or install FFmpeg manually.{RESET}")
        return None

    # Extract only ffmpeg.exe and ffprobe.exe
    print(f"{CYAN}[INFO] Extracting FFmpeg binaries...{RESET}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                base_name = os.path.basename(member).lower()
                if base_name in ('ffmpeg.exe', 'ffprobe.exe'):
                    source = zip_ref.open(member)
                    target_file = os.path.join(ffmpeg_dir, base_name)
                    with open(target_file, "wb") as target:
                        shutil.copyfileobj(source, target)
        print(f"{GREEN}[OK] FFmpeg installed successfully at: {ffmpeg_dir}{RESET}\n")
    except Exception as e:
        print(f"{RED}[ERROR] Failed to extract FFmpeg: {e}{RESET}")
    finally:
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception:
                pass

    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        return ffmpeg_dir
    return None

def fetch_resolutions(info):
    """
    Extracts available video heights from info dict and returns sorted list of integers.
    """
    formats = info.get('formats') or []
    heights = set()
    for f in formats:
        h = f.get('height')
        vcodec = f.get('vcodec') or 'none'
        if h and vcodec != 'none':
            try:
                heights.add(int(h))
            except (ValueError, TypeError):
                pass
    return sorted(list(heights))

def main():
    print_banner()

    # Step 1: URL input
    while True:
        url = input("Enter video or playlist link (or type 'U' to check updates, 'Q' to quit): ").strip()
        if not url:
            print(f"{RED}[ERROR] URL cannot be empty.{RESET}\n")
            continue
        if url.lower() in ('q', 'quit', 'exit'):
            print("\nExiting...")
            sys.exit(0)
        if url.lower() in ('u', 'update', 'check-update'):
            check_for_updates()
            continue
        break

    # Setup FFmpeg
    ffmpeg_dir = ensure_ffmpeg()
    if not ffmpeg_dir:
        print(f"{YELLOW}[WARN] Continuing without FFmpeg. 1080p+ video merging and MP3 conversion require FFmpeg.{RESET}\n")

    # Step 2: Playlist Detection (if link indicates playlist)
    is_playlist = False
    playlist_items_opt = None
    if 'list=' in url or 'playlist' in url:
        print(f"{CYAN}[INFO] Checking playlist information...{RESET}")
        try:
            ydl_check = yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': True})
            check_info = ydl_check.extract_info(url, download=False)
            if check_info.get('_type') == 'playlist' or 'entries' in check_info:
                is_playlist = True
                playlist_title = check_info.get('title', 'YouTube Playlist')
                entries = list(check_info.get('entries') or [])
                count = len(entries)
                print(f"\n{GREEN}[PLAYLIST DETECTED]{RESET} '{playlist_title}' ({count} videos)")
                print("Select playlist option:")
                print("1 - Download entire playlist (default)")
                print("2 - Download specific range (e.g. 1-5)")
                print("3 - Download only single video")
                p_choice = input("Enter choice [1-3]: ").strip()
                if p_choice == '2':
                    r_input = input(f"Enter range (e.g. 1-5, max {count}): ").strip()
                    if r_input:
                        playlist_items_opt = r_input
                elif p_choice == '3':
                    playlist_items_opt = "1"
                    is_playlist = False
        except Exception:
            is_playlist = False

    # Step 3: Video or Audio only
    print("\nSelect download mode:")
    print("1 - Video (MP4) (default)")
    print("2 - Audio only (MP3)")
    mode_input = input("Enter choice [1-2]: ").strip()
    audio_only = (mode_input == "2")

    selected_height = 720

    if not audio_only:
        # Step 4 (Video only): Fetch available video qualities
        print(f"\n{CYAN}[INFO] Fetching available video qualities...{RESET}")
        target_info = None
        try:
            ydl_inspect_opts = {
                'quiet': True,
                'no_warnings': True,
                'playlist_items': '1' if is_playlist else None,
                'extract_flat': False
            }
            if ffmpeg_dir:
                ydl_inspect_opts['ffmpeg_location'] = ffmpeg_dir
            with yt_dlp.YoutubeDL(ydl_inspect_opts) as ydl:
                full_info = ydl.extract_info(url, download=False)
                if full_info.get('_type') == 'playlist':
                    entries = list(full_info.get('entries') or [])
                    target_info = entries[0] if entries else full_info
                else:
                    target_info = full_info
        except Exception as e:
            print(f"{YELLOW}[WARN] Could not fetch detailed format list ({e}). Standard quality selection will be used.{RESET}")
            target_info = None

        available_heights = fetch_resolutions(target_info) if target_info else []
        quality_choices = []

        if available_heights:
            labels = {
                360: "360p",
                480: "480p",
                720: "720p (HD)",
                1080: "1080p (Full HD)",
                1440: "1440p (2K)",
                2160: "2160p (4K)",
                4320: "4320p (8K)"
            }
            for h in available_heights:
                lbl = labels.get(h, f"{h}p")
                quality_choices.append((lbl, h))
            quality_choices.append(("Best Available (Highest)", 99999))
        else:
            quality_choices = [
                ("360p", 360),
                ("480p", 480),
                ("720p (HD)", 720),
                ("1080p (Full HD)", 1080),
                ("Best Available (Highest)", 99999)
            ]

        # Find default index: prefer 720p
        default_idx = 1
        for idx, (lbl, h) in enumerate(quality_choices, 1):
            if h == 720:
                default_idx = idx
                break
        if default_idx == 1 and 720 not in [h for _, h in quality_choices]:
            candidates = [idx for idx, (_, h) in enumerate(quality_choices, 1) if h <= 720 and h != 99999]
            if candidates:
                default_idx = candidates[-1]

        print("\nSelect video quality:")
        for idx, (lbl, h) in enumerate(quality_choices, 1):
            is_def = " (default)" if idx == default_idx else ""
            print(f"{idx} - {lbl}{is_def}")

        vq_input = input(f"Enter choice [1-{len(quality_choices)}]: ").strip()
        selected_height = quality_choices[default_idx - 1][1]
        if vq_input.isdigit():
            c_num = int(vq_input)
            if 1 <= c_num <= len(quality_choices):
                selected_height = quality_choices[c_num - 1][1]
            else:
                print(f"{YELLOW}[WARN] Invalid choice. Using default.{RESET}")
        elif vq_input:
            print(f"{YELLOW}[WARN] Invalid input. Using default.{RESET}")

    # Step 5: Download folder
    default_dir = get_default_download_dir()
    print(f"\nEnter download folder:")
    print(f"Default: {default_dir}")
    print("Press Enter to use default, or type 'B' to browse with folder picker:")
    folder_input = input("Folder: ").strip()

    chosen_dir = default_dir
    if folder_input.lower() == 'b':
        selected = browse_folder_gui(default_dir)
        if selected:
            chosen_dir = selected
            print(f"Selected: {chosen_dir}")
        else:
            print(f"No folder selected. Using default: {chosen_dir}")
    elif folder_input:
        chosen_dir = os.path.abspath(folder_input)

    try:
        os.makedirs(chosen_dir, exist_ok=True)
    except Exception as e:
        print(f"{RED}[ERROR] Cannot create or access directory {chosen_dir}: {e}{RESET}")
        pause_and_exit(1)

    # Step 6: Start Download Immediately
    print(f"\n{CYAN}[INFO] Starting download...{RESET}\n")

    out_template = os.path.join(chosen_dir, "%(title)s.%(ext)s")
    if is_playlist:
        out_template = os.path.join(chosen_dir, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': out_template,
        'retries': 10,
        'restrictfilenames': True,
        'noplaylist': False if is_playlist else True,
    }

    if ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ffmpeg_dir

    if playlist_items_opt:
        ydl_opts['playlist_items'] = playlist_items_opt

    postprocessors = []

    if audio_only:
        # Audio mode: Fixed to MP3 with best audio quality
        ydl_opts['format'] = 'bestaudio/best'
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        })
    else:
        # Video mode: Fixed to MP4 with selected height and best audio
        if selected_height >= 99999:
            v_spec = "bestvideo+bestaudio/best"
        else:
            v_spec = f"bestvideo[height<={selected_height}]+bestaudio/best[height<={selected_height}]"
        ydl_opts['format'] = v_spec
        ydl_opts['merge_output_format'] = 'mp4'

        # Always embed subtitles and thumbnail for video
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = ['en.*', 'en']
        ydl_opts['writethumbnail'] = True

        postprocessors.append({'key': 'FFmpegMetadata'})
        postprocessors.append({'key': 'FFmpegEmbedSubtitle'})
        postprocessors.append({'key': 'EmbedThumbnail'})

    ydl_opts['postprocessors'] = postprocessors

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            exit_code = ydl.download([url])
            if exit_code == 0:
                print(f"\n{GREEN}[DONE] Download completed successfully.{RESET}")
                print(f"Saved to: {chosen_dir}")
            else:
                print(f"\n{YELLOW}[WARN] Download finished with exit code {exit_code}.{RESET}")
    except Exception as e:
        print(f"\n{RED}[ERROR] Download failed: {e}{RESET}")

    pause_and_exit(0)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}Operation cancelled by user. Exiting...{RESET}")
        sys.exit(0)
