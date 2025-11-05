# README_en.md

[Версия на русском](README.md)

## Folder to Playlists Script

This Python script scans a music directory and generates M3U8 playlists based on artist or album grouping, using metadata from audio files.

### Features
- Supports various audio formats: MP3, M4A, FLAC, OGG, OPUS, WMA, APE, AIFF, WAV, and others.
- Grouping by artists (default) or albums.
- Automatic detection of compilations based on unique artists in a folder or the compilation flag in metadata.
- Exclusion of specified directories from processing.
- Minimum number of tracks per playlist (default: 2).
- Splitting large playlists into chunks of 500 tracks.
- Cleaning grouping keys for safe filenames.
- Debug mode for verbose logging.

### Requirements
- Python 3.6+ (tested on 3.12.3).
- Mutagen library: `pip install mutagen`.

### Installation
1. Install Python if not already installed.
2. Install Mutagen: `pip install mutagen`.
3. Download the script `folder_to_playlists.py`.

### Usage
Run the script from the command line:

```
python folder_to_playlists.py [root_dir] [playlists_dir] [mode]
```

- `root_dir`: Root music directory (default: 'C:/!!Downloads/Music').
- `playlists_dir`: Directory to save playlists (default: 'C:/Users/arinoki/Desktop/playlists').
- `mode`: Grouping mode — 'artist' (by artists) or 'album' (by albums, default 'artist').

If arguments are not provided, the script will prompt for them interactively.

### Configuration
Edit constants in the script:
- `DEFAULT_ROOT_DIR`: Default root directory.
- `DEFAULT_PLAYLISTS_DIR`: Default playlists directory.
- `DEFAULT_MODE`: Default mode ('artist' or 'album').
- `DEBUG`: Enable debug logs (True/False).
- `MIN_TRACKS_PER_PLAYLIST`: Minimum tracks per playlist.
- `AUDIO_EXTS`: List of supported extensions.
- `EXCLUDED_DIRS_RAW`: List of excluded directories.
- `UNIQUE_ARTIST_THRESHOLD`: Threshold of unique artists for compilation detection.

### Examples
- Artist grouping: `python folder_to_playlists.py "C:/Music" "C:/Playlists" artist`
- Album grouping: `python folder_to_playlists.py "C:/Music" "C:/Playlists" album`

### How It Works
- In 'artist' mode: Groups tracks by albumartist or artist from metadata. For compilations, uses "Various Artists - [album or folder name]".
- In 'album' mode: Creates a playlist for each folder with audio files, using the folder name as the key.
- Skips excluded directories.
- Sorts tracks by filename.
- Outputs a summary: processed directories, skipped, created playlists.

### Limitations
- No support for installing additional packages (uses only Mutagen).
- Processes only local files.
- May take time for large collections.

### License
CC BY‑NC‑SA 4.0