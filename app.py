import os
import sys
import shutil
import zipfile
import urllib.request
import json
import re
import ctypes
from pathlib import Path

# Set UTF-8 console output and enable VT100 on Windows
if os.name == 'nt':
    os.system('')
    try:
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleTitleW("YT-DLP Advanced Downloader")
    except Exception:
        pass

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    FileSizeColumn,
    TotalFileSizeColumn,
)

console = Console(safe_box=True)

import yt_dlp

def print_banner():
    banner_text = (
        "[bold green]>>  YT-DLP ADVANCED DOWNLOADER[/bold green]\n"
        "[dim]Fast, high-quality YouTube video & MP3 audio downloader[/dim]"
    )
    console.print(Panel(banner_text, border_style="bright_green", padding=(0, 2)))
    console.print()

def pause_and_exit(code=0):
    if sys.stdin.isatty():
        console.print("[dim]Press any key to exit...[/dim]")
        try:
            import msvcrt
            msvcrt.getch()
        except Exception:
            try:
                input()
            except Exception:
                pass
    else:
        console.print("[dim][Exiting][/dim]")
    sys.exit(code)

def play_chime():
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass

def get_settings_path():
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    return os.path.join(local_app_data, "YouTubeDownloader", "settings.json")

def load_settings():
    try:
        path = get_settings_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_setting(key, value):
    try:
        path = get_settings_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        settings = load_settings()
        settings[key] = value
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

def get_default_download_dir():
    settings = load_settings()
    last_dir = settings.get("last_download_dir")
    if last_dir and os.path.isdir(last_dir):
        return last_dir
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        return str(downloads)
    return os.getcwd()

def get_clipboard_youtube_url():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get().strip()
        root.destroy()
        if text.startswith("http://") or text.startswith("https://"):
            lower = text.lower()
            if "youtube.com/" in lower or "youtu.be/" in lower:
                return text
    except Exception:
        pass
    return None

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
        console.print(f"[yellow][WARN] Could not open graphical folder picker: {e}[/yellow]")
        return None

def check_for_updates():
    console.print(f"\n[bold cyan]Checking for yt-dlp updates...[/bold cyan]")
    current_ver = yt_dlp.version.__version__
    console.print(f"Current version: [white]{current_ver}[/white]")
    try:
        req = urllib.request.Request(
            'https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode('utf-8'))
            latest_ver = data.get('tag_name', '').lstrip('v')
            if latest_ver and latest_ver != current_ver:
                console.print(f"[bold yellow][UPDATE AVAILABLE][/bold yellow] Newer version: [bold green]{latest_ver}[/bold green]")
                console.print(f"Release URL: [underline cyan]{data.get('html_url')}[/underline cyan]")
            else:
                console.print(f"[bold green][OK] You are running the latest yt-dlp engine ({current_ver}).[/bold green]")
    except Exception as e:
        console.print(f"[red][WARN] Update check failed: {e}[/red]")
    console.print()

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

    # 4. If missing, auto-download with progress
    console.print("[yellow][INFO] FFmpeg was not detected on this system.[/yellow]")
    console.print("[dim]FFmpeg is required for 1080p+ video merging and MP3 conversion.[/dim]")
    console.print("[bold green]Downloading minimal FFmpeg package (one-time setup)...[/bold green]")

    os.makedirs(ffmpeg_dir, exist_ok=True)
    zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")

    urls = [
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ]

    download_success = False
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response, open(zip_path, 'wb') as out_file:
                total_length = response.headers.get('content-length')
                total_size = int(total_length) if total_length else 0
                block_size = 64 * 1024
                downloaded = 0
                with Progress(
                    TextColumn("[bold cyan]Downloading FFmpeg"),
                    BarColumn(bar_width=30),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    "|",
                    FileSizeColumn(),
                    "/",
                    TotalFileSizeColumn(),
                    console=console
                ) as dl_prog:
                    task = dl_prog.add_task("dl", total=total_size)
                    while True:
                        buf = response.read(block_size)
                        if not buf:
                            break
                        out_file.write(buf)
                        downloaded += len(buf)
                        dl_prog.update(task, completed=downloaded)
            download_success = True
            break
        except Exception as e:
            console.print(f"[red][WARN] Download from {url} failed: {e}[/red]")
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass

    if not download_success:
        console.print("[bold red][ERROR] Could not automatically download FFmpeg. Please install FFmpeg manually.[/bold red]")
        return None

    # Extract only ffmpeg.exe and ffprobe.exe
    with console.status("[bold cyan]Extracting FFmpeg binaries...[/bold cyan]", spinner="dots"):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    base_name = os.path.basename(member).lower()
                    if base_name in ('ffmpeg.exe', 'ffprobe.exe'):
                        source = zip_ref.open(member)
                        target_file = os.path.join(ffmpeg_dir, base_name)
                        with open(target_file, "wb") as target:
                            shutil.copyfileobj(source, target)
            console.print(f"[bold green][OK] FFmpeg configured successfully at:[/] [white]{ffmpeg_dir}[/]\n")
        except Exception as e:
            console.print(f"[red][ERROR] Failed to extract FFmpeg: {e}[/red]")
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

def show_video_card(info):
    title = info.get('title', 'YouTube Video')
    uploader = info.get('uploader') or info.get('channel') or 'Unknown Channel'
    duration_sec = info.get('duration')
    if duration_sec:
        m, s = divmod(int(duration_sec), 60)
        h, m = divmod(m, 60)
        duration_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}:{s:02d}"
    else:
        duration_str = "Live / Unknown"

    view_count = info.get('view_count')
    views_str = f"{view_count:,} views" if view_count else "Unknown views"

    content = (
        f"[bold white]{title}[/bold white]\n\n"
        f"[dim]Channel:[/] [bold cyan]{uploader}[/]    "
        f"[dim]Duration:[/] [bold yellow]{duration_str}[/]    "
        f"[dim]Views:[/] [bold green]{views_str}[/]"
    )
    console.print(Panel(content, title="[bold bright_cyan]Video Details[/]", border_style="cyan", padding=(0, 2)))

class RichYtDlpProgress:
    def __init__(self, console_obj):
        self.console = console_obj
        self.progress = Progress(
            TextColumn("[bold cyan]{task.fields[filename]}", justify="left"),
            BarColumn(bar_width=25),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "|",
            FileSizeColumn(),
            "/",
            TotalFileSizeColumn(),
            "|",
            TransferSpeedColumn(),
            "|",
            TimeRemainingColumn(),
            console=self.console,
            transient=False
        )
        self.tasks = {}

    def hook(self, d):
        if d['status'] == 'downloading':
            raw_fn = os.path.basename(d.get('filename') or 'Downloading...')
            fn_display = (raw_fn[:24] + '...') if len(raw_fn) > 27 else raw_fn
            fn_key = d.get('filename') or 'main'

            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)

            if fn_key not in self.tasks:
                self.tasks[fn_key] = self.progress.add_task("dl", total=total, filename=fn_display)
            else:
                self.progress.update(self.tasks[fn_key], total=total, completed=downloaded, filename=fn_display)

        elif d['status'] == 'finished':
            fn_key = d.get('filename') or 'main'
            if fn_key in self.tasks:
                t_id = self.tasks[fn_key]
                t_total = self.progress.tasks[t_id].total
                if t_total:
                    self.progress.update(t_id, completed=t_total)

    def postprocessor_hook(self, d):
        status = d.get('status')
        pp = d.get('postprocessor')
        if status == 'started':
            if pp == 'FFmpegMerger':
                self.console.print("[dim cyan][MERGE] Merging video and audio tracks with FFmpeg...[/dim cyan]")
            elif pp == 'FFmpegExtractAudio':
                self.console.print("[dim cyan][CONVERT] Converting audio track to MP3 with FFmpeg...[/dim cyan]")
            elif pp == 'FFmpegEmbedSubtitle':
                self.console.print("[dim cyan][SUBS] Embedding subtitles into MP4...[/dim cyan]")
            elif pp == 'EmbedThumbnail':
                self.console.print("[dim cyan][THUMB] Embedding thumbnail artwork...[/dim cyan]")

def main():
    print_banner()

    # Step 1: URL input with clipboard detection
    while True:
        clipboard_url = get_clipboard_youtube_url()
        if clipboard_url:
            console.print(f"[bold cyan][CLIPBOARD] Detected YouTube link:[/] [underline white]{clipboard_url}[/]")
            url_input = console.input("[bold yellow]Press Enter to use it, or paste another link[/] [dim]('U' updates, 'Q' quit)[/]: ").strip()
            if not url_input:
                url = clipboard_url
            else:
                url = url_input
        else:
            url = console.input("[bold yellow]Enter video or playlist link[/] [dim]('U' updates, 'Q' quit)[/]: ").strip()

        if not url:
            console.print("[red][ERROR] URL cannot be empty.[/red]\n")
            continue
        if url.lower() in ('q', 'quit', 'exit'):
            console.print("\n[dim]Exiting...[/dim]")
            sys.exit(0)
        if url.lower() in ('u', 'update', 'check-update'):
            check_for_updates()
            continue
        break

    # Setup FFmpeg
    ffmpeg_dir = ensure_ffmpeg()
    if not ffmpeg_dir:
        console.print("[yellow][WARN] Continuing without FFmpeg. High resolutions (1080p+) and MP3 conversion require FFmpeg.[/yellow]\n")

    # Step 2: Playlist Detection
    is_playlist = False
    playlist_items_opt = None
    if 'list=' in url or 'playlist' in url:
        with console.status("[bold cyan]Checking playlist information...[/bold cyan]", spinner="dots"):
            try:
                ydl_check = yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': True})
                check_info = ydl_check.extract_info(url, download=False)
                if check_info.get('_type') == 'playlist' or 'entries' in check_info:
                    is_playlist = True
                    playlist_title = check_info.get('title', 'YouTube Playlist')
                    entries = list(check_info.get('entries') or [])
                    count = len(entries)
            except Exception:
                is_playlist = False

        if is_playlist:
            console.print(f"\n[bold green][PLAYLIST][/] [white]{playlist_title}[/] [dim]({count} videos)[/dim]")
            console.print(" [bold green]1[/] - Download entire playlist [bold green](default)[/]")
            console.print(" [cyan]2[/] - Download specific range (e.g. 1-5)")
            console.print(" [cyan]3[/] - Download only single video")
            p_choice = console.input("[bold yellow]Enter choice [1-3][/] [dim](press Enter for entire playlist)[/]: ").strip()
            if p_choice == '2':
                r_input = console.input(f"[bold yellow]Enter range (e.g. 1-5, max {count}):[/] ").strip()
                if r_input:
                    playlist_items_opt = r_input
            elif p_choice == '3':
                playlist_items_opt = "1"
                is_playlist = False

    # Step 3: Video or Audio only
    console.print("\n[bold cyan]Select download mode:[/bold cyan]")
    console.print(" [bold green]1[/] - [bold white]Video (MP4)[/] [bold green](default)[/]")
    console.print(" [cyan]2[/] - Audio only (MP3)")
    mode_input = console.input("[bold yellow]Enter choice [1-2][/] [dim](press Enter for Video)[/]: ").strip()
    audio_only = (mode_input == "2")

    selected_height = 720

    if not audio_only:
        # Step 4: Video Mode - Fetch details and qualities with spinner
        target_info = None
        with console.status("[bold cyan]Fetching video details & available qualities...[/bold cyan]", spinner="dots"):
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
                target_info = None

        if target_info:
            console.print()
            show_video_card(target_info)

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

        # Find default index (prefer 720p)
        default_idx = 1
        for idx, (lbl, h) in enumerate(quality_choices, 1):
            if h == 720:
                default_idx = idx
                break
        if default_idx == 1 and 720 not in [h for _, h in quality_choices]:
            candidates = [idx for idx, (_, h) in enumerate(quality_choices, 1) if h <= 720 and h != 99999]
            if candidates:
                default_idx = candidates[-1]

        console.print("\n[bold cyan]Select video quality:[/bold cyan]")
        for idx, (lbl, h) in enumerate(quality_choices, 1):
            if idx == default_idx:
                console.print(f" [bold green]{idx}[/] - [bold white]{lbl}[/] [bold green](default)[/]")
            else:
                console.print(f" [cyan]{idx}[/] - {lbl}")

        vq_input = console.input(f"[bold yellow]Enter choice [1-{len(quality_choices)}][/] [dim](press Enter for default)[/]: ").strip()
        selected_height = quality_choices[default_idx - 1][1]
        if vq_input.isdigit():
            c_num = int(vq_input)
            if 1 <= c_num <= len(quality_choices):
                selected_height = quality_choices[c_num - 1][1]
            else:
                console.print(f"[yellow][WARN] Invalid choice. Using default ({quality_choices[default_idx - 1][0]}).[/yellow]")
        elif vq_input:
            console.print(f"[yellow][WARN] Invalid input. Using default ({quality_choices[default_idx - 1][0]}).[/yellow]")

    # Step 5: Destination folder with persistent memory
    default_dir = get_default_download_dir()
    console.print(f"\n[bold cyan]Download Folder:[/] [white underline]{default_dir}[/]")
    folder_input = console.input("[bold yellow]Press Enter for default, or type 'B' to browse with folder picker:[/] ").strip()

    chosen_dir = default_dir
    if folder_input.lower() == 'b':
        selected = browse_folder_gui(default_dir)
        if selected:
            chosen_dir = selected
            console.print(f"[green][OK] Selected folder:[/] [white]{chosen_dir}[/]")
        else:
            console.print(f"[dim]No folder selected. Using default: {chosen_dir}[/dim]")
    elif folder_input:
        chosen_dir = os.path.abspath(folder_input)

    try:
        os.makedirs(chosen_dir, exist_ok=True)
        # Remember this folder for future runs
        save_setting("last_download_dir", chosen_dir)
    except Exception as e:
        console.print(f"[bold red][ERROR] Cannot access directory {chosen_dir}: {e}[/bold red]")
        pause_and_exit(1)

    # Step 6: Start Download Immediately with Rich Progress Bar
    console.print(f"\n[bold green]>> Starting download...[/bold green]\n")

    out_template = os.path.join(chosen_dir, "%(title)s.%(ext)s")
    if is_playlist:
        out_template = os.path.join(chosen_dir, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")

    progress_handler = RichYtDlpProgress(console)

    ydl_opts = {
        'outtmpl': out_template,
        'retries': 10,
        'restrictfilenames': True,
        'noplaylist': False if is_playlist else True,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'progress_hooks': [progress_handler.hook],
        'postprocessor_hooks': [progress_handler.postprocessor_hook],
    }

    if ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ffmpeg_dir

    if playlist_items_opt:
        ydl_opts['playlist_items'] = playlist_items_opt

    postprocessors = []

    if audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        })
    else:
        if selected_height >= 99999:
            v_spec = "bestvideo+bestaudio/best"
        else:
            v_spec = f"bestvideo[height<={selected_height}]+bestaudio/best[height<={selected_height}]"
        ydl_opts['format'] = v_spec
        ydl_opts['merge_output_format'] = 'mp4'

        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = ['en.*', 'en']
        ydl_opts['writethumbnail'] = True

        postprocessors.append({'key': 'FFmpegMetadata'})
        postprocessors.append({'key': 'FFmpegEmbedSubtitle'})
        postprocessors.append({'key': 'EmbedThumbnail'})

    ydl_opts['postprocessors'] = postprocessors

    try:
        with progress_handler.progress:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                exit_code = ydl.download([url])

        if exit_code == 0:
            play_chime()
            console.print(f"\n[bold green][DONE] Download completed successfully![/bold green]")
            console.print(f"[dim]Saved to:[/] [cyan underline]{chosen_dir}[/]\n")
        else:
            console.print(f"\n[yellow][WARN] Download finished with exit code {exit_code}.[/yellow]\n")
    except Exception as e:
        console.print(f"\n[bold red][ERROR] Download failed: {e}[/bold red]\n")

    pause_and_exit(0)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print(f"\n[yellow]Operation cancelled by user. Exiting...[/yellow]")
        sys.exit(0)
