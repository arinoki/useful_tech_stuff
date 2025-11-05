# README_en.md

# YouTube Music Playlist Downloader to M4A

This script downloads playlists or single videos from YouTube/YouTube Music to M4A format (audio with metadata and embedded thumbnails). It supports asynchronous parallel downloads, SponsorBlock for removing sponsor segments, and handling private/age-restricted content via cookies. Uses **yt-dlp** for extraction and **FFmpeg** for post-processing.

The script saves files with numbering (for playlists), adds tags (artist, title, thumbnail), and skips errors to continue downloading.

## Requirements

- Python 3.8+ (for asyncio support).
- Dependencies: `pip install yt-dlp`.
- **FFmpeg**: Install from [official site](https://ffmpeg.org/download.html) and add to PATH (required for audio extraction, thumbnail embedding, and metadata).
- Cookies file: Export YouTube cookies from your browser (Chrome/Firefox) in Netscape format (cookies.txt). Use the [cookies.txt extension](https://chromewebstore.google.com/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg) for Chrome.

## Setup

1. **Install dependencies**:
   ```
   pip install yt-dlp
   ```

2. **Configure cookies**:
   - Export YouTube cookies to `cookies.txt` (Netscape format).
   - Set the path in the script: `COOKIES_FILE = Path("your/path/to/cookies.txt")`.
   - Cookies are needed for private playlists or 18+ content.

3. **Optional parameters**:
   - `CONCURRENT_DOWNLOADS_LIMIT`: Number of concurrent downloads (default: 8).
   - Logging: INFO level by default; adjust via `logging` in code.

## Usage

```bash
python youtube_music_playlist.py <playlist_or_video_URL>
```

- `<URL>`: Link to a YouTube Music playlist, YouTube playlist, or single video (e.g., `https://music.youtube.com/playlist?list=PL...`).
- Creates a folder named after the playlist (sanitized) in the current directory.
- Files saved as `001. Artist - Title.m4a` (numbered for playlists).

Example:
```bash
python youtube_music_playlist.py "https://music.youtube.com/playlist?list=PL123456789"
```

The script:
- Extracts playlist info (title, video list).
- Downloads best-quality audio to M4A.
- Embeds thumbnails and metadata.
- Removes sponsor segments (SponsorBlock).
- Handles errors (skips problematic videos).

## Example Output

```
2025-11-05 10:00:00,123 - INFO - Получение информации о плейлисте: https://music.youtube.com/playlist?list=PL...
2025-11-05 10:00:05,456 - INFO - Плейлист 'My Favorite Songs' будет загружен в: /path/to/My_Favorite_Songs
2025-11-05 10:00:05,789 - INFO - Найдено 26 видео для загрузки.
2025-11-05 10:00:06,012 - INFO - Начинается загрузка видео abc123 (Индекс: 1) через yt-dlp библиотеку...
[download] abc123: Downloading webpage
[ExtractAudio] Destination: 001. Artist - Title.m4a
[download] 100% of 5.23MiB in 00:15
[EmbedThumbnail] Embedding thumbnail in 001. Artist - Title.m4a
[FFmpegMetadata] Adding metadata to 001. Artist - Title.m4a
2025-11-05 10:00:21,345 - INFO - Видео abc123 (Индекс: 1) успешно загружено.
...
2025-11-05 10:05:00,678 - INFO - Все загрузки завершены для плейлиста 'My Favorite Songs'.
```

## Limitations

- Requires FFmpeg in PATH; without it, post-processing (thumbnails/metadata) fails.
- Cookies expire on logout; re-export as needed.
- Audio-only (M4A); no video download.
- Skips errors (e.g., deleted videos) but doesn't resume interrupted downloads.
- SponsorBlock works for supported videos; may miss some segments.
- Parallel downloads may strain network/CPU; reduce `CONCURRENT_DOWNLOADS_LIMIT` if needed.

## License

This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en).  
Attribution: © Arinoki, 2025.  
Distribution only in unmodified form, non-commercial use only.