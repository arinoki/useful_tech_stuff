[Версия на русском](README.md)

## Description

This Python script is designed to automate the creation of M3U8 playlists from your music collection. It recursively traverses the specified root folder, extracts the artist metadata from audio files (using the mutagen library), and groups tracks by artists. For each artist, one or more playlists are created (if there are more than 500 tracks, it splits into parts with numbering). Paths to tracks in playlists are absolute.

Supported audio formats: MP3, OPUS, OGG, M4A, FLAC, WAV, AAC, WMA, APE, ALAC, AIFF.

### Features
- Grouping tracks by artist based on metadata ( "artist" tag).
- Splitting playlists into chunks of 500 tracks (e.g., "Artist.m3u8", "Artist_2.m3u8").
- Excluding specified folders (default: "!!youtube", configurable).
- If the root folder matches an excluded one, the exclusion is ignored.
- Sorting tracks by filename.
- Interactive input for paths on launch (or via command-line arguments).
- Error handling and UTF-8 support for Cyrillic and special characters.

### Requirements
- Python 3.x (tested on 3.12+).
- `mutagen` library for reading metadata: install via `pip install mutagen`.

Standard libraries: `os`, `sys`, `collections`.

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/arinoki/useful_tech_stuff.git
   ```
2. Install dependencies:
   ```
   pip install mutagen
   ```

### Usage
Run the script:
```
python folder_to_playlists.py [root_dir] [playlists_dir]
```
- If arguments are not provided, the script will prompt interactively (press Enter for defaults).
- Default root folder: `C:/!!Downloads/Music`.
- Default playlists folder: `C:/Users/arinoki/Desktop/playlists`.

#### Configuration
In the script, you can customize:
- `DEFAULT_ROOT_DIR`: Default root folder.
- `DEFAULT_PLAYLISTS_DIR`: Default playlists folder.
- `AUDIO_EXTS`: List of audio file extensions.
- `EXCLUDED_DIRS`: List of absolute paths to excluded folders (e.g., for "!!youtube").

If metadata is missing or unreadable, the artist is marked as "Unknown".

### Example
Assume your structure:
```
C:/!!Downloads/Music/
├── Artist1/
│   └── Album1/
│       ├── track1.mp3
│       └── track2.flac
└── Artist2/
    └── track3.ogg
```
The script will create:
- `Artist1.m3u8` with absolute paths to track1 and track2.
- `Artist2.m3u8` with path to track3.

If "!!youtube" contains files, they will be skipped unless specified as root_dir.

### License
CC BY‑NC‑SA 4.0

### Author
Arinoki