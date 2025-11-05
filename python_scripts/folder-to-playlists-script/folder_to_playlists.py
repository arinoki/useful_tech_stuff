import os
import sys
import re
from collections import defaultdict

# For mutagen
import mutagen
from mutagen.easyid3 import EasyID3  # MP3
from mutagen.mp4 import MP4  # M4A, AAC, ALAC
from mutagen.flac import FLAC  # FLAC
from mutagen.oggvorbis import OggVorbis  # OGG, OPUS
from mutagen.asf import ASF  # WMA
from mutagen.apev2 import APEv2  # APE
from mutagen.aiff import AIFF  # AIFF
from mutagen.wave import WAVE  # WAV

# Default values
DEFAULT_ROOT_DIR = 'C:/!!Downloads/Music'
DEFAULT_PLAYLISTS_DIR = 'C:/Users/arinoki/Desktop/playlists'
DEFAULT_MODE = 'artist'  # 'artist' or 'album'
DEBUG = True  # Set to False to disable verbose logging
MIN_TRACKS_PER_PLAYLIST = 2  # Don't create playlists with fewer tracks

# List of audio extensions (case-insensitive)
AUDIO_EXTS = [
    '.mp3', '.opus', '.ogg', '.m4a', '.flac',
    '.wav', '.aac', '.wma', '.ape', '.alac', '.aiff'
]

# Excluded directories (case-insensitive, normalized paths)
EXCLUDED_DIRS_RAW = [
    'C:/!!Downloads/Music/!!youtube',
    'C:/!!Downloads/Music/!!anime',
    'C:/!!Downloads/Music/!!!Mia2',
    'C:/!!Downloads/Music/!!games',
    'C:/!!Downloads/Music/!!Radio Maximum',
    'C:/!!Downloads/Music/!!temp',
    'C:/!!Downloads/Music/!!movies',
    # Add more if needed
]
EXCLUDED_DIRS = set(os.path.normpath(os.path.abspath(d)).lower() for d in EXCLUDED_DIRS_RAW)

# Threshold for detecting compilations based on unique artists in a folder
UNIQUE_ARTIST_THRESHOLD = 2  # If >= this number of unique artists in a dir, treat as compilation

def get_metadata(file_path, key):
    """
    Generic metadata extractor for artist, albumartist, album, compilation.
    Returns first item if list, or None/False.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        audio = None
        if ext == '.mp3':
            audio = EasyID3(file_path)
        elif ext in ('.m4a', '.aac', '.alac'):
            audio = MP4(file_path)
        elif ext == '.flac':
            audio = FLAC(file_path)
        elif ext in ('.ogg', '.opus'):
            audio = OggVorbis(file_path)
        elif ext == '.wma':
            audio = ASF(file_path)
        elif ext == '.ape':
            audio = APEv2(file_path)
        elif ext == '.aiff':
            audio = AIFF(file_path)
        elif ext == '.wav':
            audio = WAVE(file_path)

        if audio is None:
            return None if key != 'compilation' else False

        value = None
        if ext == '.mp3':
            if key == 'albumartist':
                value = audio.get('albumartist', None)
            elif key == 'artist':
                value = audio.get('artist', None)
            elif key == 'album':
                value = audio.get('album', None)
            elif key == 'compilation':
                return audio.get('compilation', ['0'])[0] == '1'
        elif ext in ('.m4a', '.aac', '.alac'):
            if key == 'albumartist':
                value = audio.get('aART', None)
            elif key == 'artist':
                value = audio.get('\xa9ART', None)
            elif key == 'album':
                value = audio.get('\xa9alb', None)
            elif key == 'compilation':
                return audio.get('cpil', [False])[0]
        elif ext == '.flac':
            if key == 'albumartist':
                value = audio.get('albumartist', None)
            elif key == 'artist':
                value = audio.get('artist', None)
            elif key == 'album':
                value = audio.get('album', None)
            elif key == 'compilation':
                return 'compilation' in audio and audio['compilation'] == ['1']
        elif ext in ('.ogg', '.opus'):
            if key == 'albumartist':
                value = audio.get('albumartist', None)
            elif key == 'artist':
                value = audio.get('artist', None)
            elif key == 'album':
                value = audio.get('album', None)
            elif key == 'compilation':
                return 'compilation' in audio and audio['compilation'] == ['1']
        elif ext == '.wma':
            if key == 'albumartist':
                value = audio.get('WM/AlbumArtist', None)
            elif key == 'artist':
                value = audio.get('Author', None)
            elif key == 'album':
                value = audio.get('WM/AlbumTitle', None)
            elif key == 'compilation':
                return False
        elif ext == '.ape':
            if key == 'albumartist':
                value = audio.get('Album Artist', None)
            elif key == 'artist':
                value = audio.get('Artist', None)
            elif key == 'album':
                value = audio.get('Album', None)
            elif key == 'compilation':
                return 'Compilation' in audio and audio['Compilation'] == ['1']
        elif ext == '.aiff':
            if key == 'albumartist':
                value = audio.get('TPE2', None)
            elif key == 'artist':
                value = audio.get('TPE1', None)
            elif key == 'album':
                value = audio.get('TALB', None)
            elif key == 'compilation':
                return False
        elif ext == '.wav':
            if key == 'albumartist':
                value = audio.get('TPE2', None)
            elif key == 'artist':
                value = audio.get('TPE1', None)
            elif key == 'album':
                value = audio.get('TALB', None)
            elif key == 'compilation':
                return False

        if isinstance(value, list) and value:
            return value[0]
        return value
    except Exception:
        return None if key != 'compilation' else False

def get_group_key(file_path, dir_name):
    """
    Get grouping key: prefer albumartist, fallback to artist, then parse filename/dir_name.
    If 'Various Artists' or compilation, use 'Various Artists - album or dir_name'.
    """
    albumartist = get_metadata(file_path, 'albumartist')
    artist = get_metadata(file_path, 'artist')
    album = get_metadata(file_path, 'album')
    is_compilation = get_metadata(file_path, 'compilation')

    key = albumartist or artist

    if not key:
        # Fallback to parse filename
        filename = os.path.splitext(os.path.basename(file_path))[0]
        filename = filename.lstrip(' -.0123456789')
        if ' - ' in filename:
            parts = filename.split(' - ', 1)
            possible_artist = parts[0].strip()
            if possible_artist and not possible_artist[0].isdigit():
                key = possible_artist
        else:
            # Clean dir_name: remove year like (2023) or [2023]
            cleaned_dir = re.sub(r'\s*[\(\[]\d{4}[\)\]]', '', dir_name).strip()
            if ' - ' in cleaned_dir:
                key = cleaned_dir.split(' - ')[0].strip(' ([')
            else:
                key = cleaned_dir.strip(' ([')

    if not key:
        key = 'Unknown'

    if key.lower() in ('various artists', 'various') or is_compilation:
        suffix = album or dir_name
        key = f"Various Artists - {suffix}"

    # Clean key for filename
    key = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in str(key))
    return key or 'Unknown'

def create_playlist(group_key, audio_files, playlists_dir):
    if len(audio_files) < MIN_TRACKS_PER_PLAYLIST:
        if DEBUG:
            print(f"Skipping small playlist: {group_key} ({len(audio_files)} tracks)")
        return

    # Sort by filename
    audio_files = sorted(list(audio_files), key=lambda x: os.path.basename(x))

    # Split into chunks of 500
    chunk_size = 10000
    for i in range(0, len(audio_files), chunk_size):
        chunk = audio_files[i:i + chunk_size]
        part_num = f"_{i // chunk_size + 1}" if i > 0 else ""
        playlist_name = f"{group_key}{part_num}.m3u8"
        playlist_path = os.path.join(playlists_dir, playlist_name)

        with open(playlist_path, 'w', encoding='utf-8') as pl_file:
            pl_file.write('#EXTM3U\n')
            for track in chunk:
                pl_file.write(track + '\n')

        print(f"Created playlist: {playlist_path}")

def main():
    # Print excluded for debugging
    if DEBUG:
        print("Excluded directories (normalized lower):")
        for ex in EXCLUDED_DIRS:
            print(ex)

    # Get root_dir, playlists_dir, mode: from args, or interactive, or default
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir_input = input(f"Enter root directory (default: {DEFAULT_ROOT_DIR}): ").strip()
        root_dir = root_dir_input if root_dir_input else DEFAULT_ROOT_DIR

    if len(sys.argv) > 2:
        playlists_dir = sys.argv[2]
    else:
        playlists_dir_input = input(f"Enter playlists directory (default: {DEFAULT_PLAYLISTS_DIR}): ").strip()
        playlists_dir = playlists_dir_input if playlists_dir_input else DEFAULT_PLAYLISTS_DIR

    if len(sys.argv) > 3:
        mode = sys.argv[3].lower()
    else:
        mode_input = input(f"Enter mode ('artist' or 'album', default: {DEFAULT_MODE}): ").strip().lower()
        mode = mode_input if mode_input else DEFAULT_MODE

    # Normalize root_dir to absolute
    root_dir = os.path.abspath(root_dir)
    if DEBUG:
        print(f"Root dir normalized: {os.path.normpath(root_dir).lower()}")

    # Ensure playlists_dir exists
    os.makedirs(playlists_dir, exist_ok=True)

    processed_dirs = 0
    skipped_dirs = 0
    created_playlists = 0

    if mode == 'album':
        # Album mode: group by folder name
        for dirpath, dirnames, filenames in os.walk(root_dir):
            processed_dirs += 1
            abs_dirpath = os.path.normpath(os.path.abspath(dirpath)).lower()
            if DEBUG:
                print(f"Checking dir: {abs_dirpath}")
            if abs_dirpath in EXCLUDED_DIRS and abs_dirpath != os.path.normpath(root_dir).lower():
                if DEBUG:
                    print(f"Skipping excluded dir: {dirpath}")
                skipped_dirs += 1
                dirnames[:] = []
                continue

            audio_files = set(os.path.abspath(os.path.join(dirpath, f)).replace('\\', '/') 
                             for f in filenames if os.path.splitext(f)[1].lower() in AUDIO_EXTS)
            if audio_files:
                group_key = os.path.basename(dirpath)
                create_playlist(group_key, audio_files, playlists_dir)
                created_playlists += 1
    else:
        # Artist mode: group by metadata key, with per-folder compilation detection
        group_to_tracks = defaultdict(set)  # Use set to avoid duplicates

        for dirpath, dirnames, filenames in os.walk(root_dir):
            processed_dirs += 1
            abs_dirpath = os.path.normpath(os.path.abspath(dirpath)).lower()
            if DEBUG:
                print(f"Checking dir: {abs_dirpath}")
            if abs_dirpath in EXCLUDED_DIRS and abs_dirpath != os.path.normpath(root_dir).lower():
                if DEBUG:
                    print(f"Skipping excluded dir: {dirpath}")
                skipped_dirs += 1
                dirnames[:] = []
                continue

            dir_name = os.path.basename(dirpath)

            audio_files = set()
            for f in filenames:
                if os.path.splitext(f)[1].lower() in AUDIO_EXTS:
                    full_path = os.path.abspath(os.path.join(dirpath, f)).replace('\\', '/')
                    audio_files.add(full_path)

            if not audio_files:
                continue

            # Detect if this folder is a compilation based on unique artists or compilation flag
            unique_artists = set()
            has_compilation_flag = False
            for full_path in audio_files:
                aa = get_metadata(full_path, 'albumartist') or get_metadata(full_path, 'artist') or 'Unknown'
                unique_artists.add(str(aa).lower())  # Case-insensitive unique
                if get_metadata(full_path, 'compilation'):
                    has_compilation_flag = True

            is_compilation_folder = len(unique_artists) >= UNIQUE_ARTIST_THRESHOLD or has_compilation_flag

            if is_compilation_folder:
                # Treat whole folder as one group, use common album if available, else dir_name
                common_album = None
                albums = set()
                for full_path in audio_files:
                    alb = get_metadata(full_path, 'album')
                    if alb:
                        albums.add(str(alb).lower())
                if len(albums) == 1:
                    common_album = next(iter(albums)).title()  # Use title case for niceness
                group_key = common_album or dir_name
                group_key = f"Various Artists - {group_key}" if group_key else 'Unknown Compilation'
                for full_path in audio_files:
                    group_to_tracks[group_key].add(full_path)
            else:
                # Normal per-track grouping
                for full_path in audio_files:
                    group_key = get_group_key(full_path, dir_name)
                    group_to_tracks[group_key].add(full_path)

        # Create playlists
        for group_key, tracks in group_to_tracks.items():
            create_playlist(group_key, tracks, playlists_dir)
            created_playlists += 1

    # Summary
    print(f"Summary: Processed {processed_dirs} dirs, skipped {skipped_dirs} excluded, created {created_playlists} playlists.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")