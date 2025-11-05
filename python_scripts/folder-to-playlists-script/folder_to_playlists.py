import os
import sys
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

# List of audio extensions (case-insensitive)
AUDIO_EXTS = [
    '.mp3', '.opus', '.ogg', '.m4a', '.flac',
    '.wav', '.aac', '.wma', '.ape', '.alac', '.aiff'
]

# Excluded directories (full paths or relative, but better full for accuracy)
EXCLUDED_DIRS = [
    os.path.abspath('C:/!!Downloads/Music/!!youtube')  # Example; adjust as needed
    # Add more if needed
]

def get_artist(file_path):
    """
    Extract artist from audio file metadata.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.mp3':
            audio = EasyID3(file_path)
            return audio.get('artist', ['Unknown'])[0]
        elif ext in ('.m4a', '.aac', '.alac'):
            audio = MP4(file_path)
            return audio.get('\xa9ART', ['Unknown'])[0]
        elif ext == '.flac':
            audio = FLAC(file_path)
            return audio.get('artist', ['Unknown'])[0]
        elif ext in ('.ogg', '.opus'):
            audio = OggVorbis(file_path)
            return audio.get('artist', ['Unknown'])[0]
        elif ext == '.wma':
            audio = ASF(file_path)
            return audio.get('WM/AlbumArtist', audio.get('Author', ['Unknown']))[0]
        elif ext == '.ape':
            audio = APEv2(file_path)
            return audio.get('Artist', ['Unknown'])[0]
        elif ext == '.aiff':
            audio = AIFF(file_path)
            return audio.get('TPE1', ['Unknown']).text[0]
        elif ext == '.wav':
            audio = WAVE(file_path)
            if 'TPE1' in audio:
                return audio['TPE1'].text[0]
            return 'Unknown'
        else:
            return 'Unknown'
    except Exception:
        return 'Unknown'

def create_artist_playlist(artist, audio_files, playlists_dir):
    if not audio_files:
        return

    # Sort by filename
    audio_files.sort(key=lambda x: os.path.basename(x))

    # Split into chunks of 500
    chunk_size = 500
    for i in range(0, len(audio_files), chunk_size):
        chunk = audio_files[i:i + chunk_size]
        part_num = f"_{i // chunk_size + 1}" if i > 0 else ""
        playlist_name = f"{artist}{part_num}.m3u8"
        playlist_path = os.path.join(playlists_dir, playlist_name)

        with open(playlist_path, 'w', encoding='utf-8') as pl_file:
            pl_file.write('#EXTM3U\n')
            for track in chunk:
                pl_file.write(track + '\n')

        print(f"Created playlist: {playlist_path}")

def main():
    # Get root_dir and playlists_dir: from args, or interactive, or default
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

    # Normalize root_dir to absolute
    root_dir = os.path.abspath(root_dir)

    # Ensure playlists_dir exists
    os.makedirs(playlists_dir, exist_ok=True)

    # Collect tracks, grouping by artist
    artist_to_tracks = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check for excluded dirs
        abs_dirpath = os.path.abspath(dirpath)
        if abs_dirpath in EXCLUDED_DIRS and abs_dirpath != root_dir:
            # Skip this dir and its subdirs
            dirnames[:] = []  # Prevent descending into subdirs
            continue

        for f in filenames:
            if os.path.splitext(f)[1].lower() in AUDIO_EXTS:
                full_path = os.path.abspath(os.path.join(dirpath, f)).replace('\\', '/')
                artist = get_artist(full_path)
                artist_to_tracks[artist].append(full_path)

    # Create playlists
    for artist, tracks in artist_to_tracks.items():
        create_artist_playlist(artist, tracks, playlists_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
