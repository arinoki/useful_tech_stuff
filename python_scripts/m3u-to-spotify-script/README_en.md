# README_en.md

# M3U Playlists Import to Spotify

This repository contains scripts to import local M3U/M3U8 playlists into Spotify. The main script extracts metadata (tags) from audio files in various formats (MP3, OGG, Opus, M4A, FLAC, and others), searches for matching tracks in Spotify, and creates a new playlist. The wrapper allows processing all playlists in a specified directory.

Format support is provided by the **mutagen** library, replacing eyed3 for compatibility with non-MP3 files.

## Requirements

- Python 3.6+.
- Dependencies: `pip install spotipy termcolor mutagen`.

## Setup

1. **Spotify API credentials**:
   - Register at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create an app and get `CLIENT_ID` and `CLIENT_SECRET`.
   - Set environment variables:
     - Windows (PowerShell): `setx SPOTIPY_CLIENT_ID "your-client-id"` and similarly for `SPOTIPY_CLIENT_SECRET`.
     - Linux/Mac: `export SPOTIPY_CLIENT_ID="your-client-id"` and similarly for `SPOTIPY_CLIENT_SECRET`.
   - `SPOTIPY_REDIRECT_URI` default: `http://127.0.0.1:8888/callback` (can be overridden).

2. Copy the scripts to one folder.

## Usage

### Main Script: `import-m3u-to-spotify.py`

```bash
python import-m3u-to-spotify.py -f "path/to/playlist.m3u8" -u your-spotify-username [-d]
```

- `-f`: Path to M3U file (required).
- `-u`: Spotify username (required).
- `-d`: Debug mode (optional, logs tags and search).

The script:
- Parses M3U, resolves file paths relative to playlist or current directory.
- Reads tags (artist/title) from files.
- If tags missing, guesses from filename (using `-` or `_` separator).
- Searches Spotify (match threshold: 50%).
- Creates a private playlist named after the file.

### Wrapper: `batch-import-m3u.py`

```bash
python batch-import-m3u.py [-u your-spotify-username] [-dir "path/to/playlists"] [-d]
```

- `-u`: Spotify username (interactive if not provided).
- `-dir`: Directory with playlists (interactive, default: `~/Desktop/playlists`).
- `-d`: Debug mode for all scripts.

Processes all `.m3u`/`.m3u8` files in the directory sequentially.

## Example Output

```
Logged-in As: Your Name (your-username)
Parsed 26 tracks from path/to/playlist.m3u8

'C:\path\to\song.opus'
Tag data: 'Artist' - 'Title'
Guess from filename: Not required
Spotify: 'Artist' - 'Title', spotify:track:id [green]

26/26 of tracks matched on Spotify, creating playlist "playlist.m3u8" on Spotify... done
```

## Limitations

- Searches by artist + title; unmatched tracks are skipped.
- Playlists created as private; tracks added in batches of 100.
- Only basic tags (artist/title); no albums/duration used.

## License

This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en).  
Attribution: © Arinoki, 2025.  
Distribution only in unmodified form, non-commercial use only.