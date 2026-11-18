@echo off
setlocal EnableDelayedExpansion
title YT-DLP Advanced Downloader
color 0A

echo =========================================
echo        YT-DLP Advanced Downloader
echo =========================================
echo.

:: -------------------------------
:: URL INPUT (REQUIRED)
:: -------------------------------
set URL=
set /p URL=Enter video or playlist link: 
if "%URL%"=="" (
    echo [ERROR] URL cannot be empty.
    pause
    exit /b
)

:: -------------------------------
:: VIDEO QUALITY
:: -------------------------------
echo.
echo Select video quality:
echo 1 - 360p
echo 2 - 480p
echo 3 - 720p (default)
echo 4 - 1080p
set /p VQ=Enter choice [1-4]: 

if "%VQ%"=="" set VQ=3
if "%VQ%"=="1" set VHEIGHT=360
if "%VQ%"=="2" set VHEIGHT=480
if "%VQ%"=="3" set VHEIGHT=720
if "%VQ%"=="4" set VHEIGHT=1080

if not defined VHEIGHT (
    echo [WARN] Invalid input. Using 720p.
    set VHEIGHT=720
)

:: -------------------------------
:: AUDIO QUALITY
:: -------------------------------
echo.
echo Select audio quality:
echo 1 - Best (default)
echo 2 - Medium (128 kbps)
echo 3 - Low (64 kbps)
set /p AQ=Enter choice [1-3]: 

if "%AQ%"=="" set AQ=1
if "%AQ%"=="1" set AOPT=bestaudio
if "%AQ%"=="2" set AOPT=bestaudio[abr<=128]
if "%AQ%"=="3" set AOPT=bestaudio[abr<=64]

if not defined AOPT (
    echo [WARN] Invalid input. Using best audio.
    set AOPT=bestaudio
)

:: -------------------------------
:: AUDIO-ONLY MODE
:: -------------------------------
echo.
set /p AUDIOONLY=Audio only mode? (y/n) [n]: 
if /I "%AUDIOONLY%"=="y" (
    set MODE=audio
) else (
    set MODE=video
)

:: -------------------------------
:: SUBTITLES
:: -------------------------------
echo.
set /p SUBS=Download subtitles? (y/n) [n]: 
set SUBOPT=
if /I "%SUBS%"=="y" (
    set SUBOPT=--write-subs --embed-subs --sub-lang "en.*"
)

:: -------------------------------
:: OUTPUT FORMAT
:: -------------------------------
echo.
echo Select output format:
echo 1 - MP4 (default)
echo 2 - MKV
set /p FMT=Enter choice [1-2]: 

if "%FMT%"=="" set FMT=1
if "%FMT%"=="1" set OUTFMT=mp4
if "%FMT%"=="2" set OUTFMT=mkv

if not defined OUTFMT (
    echo [WARN] Invalid input. Using MP4.
    set OUTFMT=mp4
)

:: -------------------------------
:: DOWNLOAD FOLDER
:: -------------------------------
echo.
set /p ODIR=Enter download folder (leave empty for current): 
if "%ODIR%"=="" (
    set ODIR=%CD%
)
if not exist "%ODIR%" (
    echo [ERROR] Folder does not exist.
    pause
    exit /b
)

:: -------------------------------
:: OPTIONAL FEATURES
:: -------------------------------
echo.
set /p LIMIT=Limit download speed? (e.g. 2M) [no]: 
set RATEOPT=
if not "%LIMIT%"=="" set RATEOPT=--limit-rate %LIMIT%

set /p RETRIES=Retry count [10]: 
if "%RETRIES%"=="" set RETRIES=10

set /p COOKIES=Cookies file path (optional): 
set COOKIEOPT=
if not "%COOKIES%"=="" set COOKIEOPT=--cookies "%COOKIES%"

:: -------------------------------
:: SUMMARY
:: -------------------------------
cls
echo =========================================
echo              DOWNLOAD SUMMARY
echo =========================================
echo URL            : %URL%
echo Mode           : %MODE%
echo Video Quality  : %VHEIGHT%p
echo Audio Quality  : %AOPT%
echo Subtitles      : %SUBS%
echo Format         : %OUTFMT%
echo Folder         : %ODIR%
echo Retries        : %RETRIES%
echo Speed Limit    : %LIMIT%
echo =========================================
echo.

pause

:: -------------------------------
:: EXECUTION
:: -------------------------------
echo [INFO] Download started...
echo.

if "%MODE%"=="audio" (
    yt-dlp ^
     -f %AOPT% ^
     --extract-audio ^
     --audio-format mp3 ^
     --audio-quality 0 ^
     %COOKIEOPT% ^
     %RATEOPT% ^
     --retries %RETRIES% ^
     -o "%ODIR%\%%(title)s.%%(ext)s" ^
     "%URL%"
) else (
    yt-dlp ^
     -f "bestvideo[height<=%VHEIGHT%]+%AOPT%/best[height<=%VHEIGHT%]" ^
     --merge-output-format %OUTFMT% ^
     %SUBOPT% ^
     --embed-thumbnail ^
     %COOKIEOPT% ^
     %RATEOPT% ^
     --retries %RETRIES% ^
     --progress ^
     --restrict-filenames ^
     -o "%ODIR%\%%(title)s.%%(ext)s" ^
     "%URL%"
)

echo.
echo [DONE] Download completed.
pause
