#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys

def parse_arguments():
    p = argparse.ArgumentParser(description='Batch wrapper to import multiple m3u playlists into Spotify')
    p.add_argument('-u', '--username', help='Spotify username (will prompt if not provided)')
    p.add_argument('-dir', '--directory', help='Directory with m3u/m3u8 playlists (will prompt if not provided)')
    p.add_argument('-d', '--debug', help='Debug mode for the import script', action='store_true', default=False)
    return p.parse_args()

def get_input(prompt, default=None):
    """Интерактивный ввод с дефолтом."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    return value if value else default

if __name__ == "__main__":
    args = parse_arguments()

    # Интерактивный ввод, если не переданы аргументы
    spotify_username = args.username or get_input("Enter Spotify username")
    if not spotify_username:
        print("Spotify username is required.")
        sys.exit(1)

    playlist_dir = args.directory or get_input("Enter directory with playlists", default=os.path.join(os.path.expanduser("~"), "Desktop", "playlists"))
    if not playlist_dir or not os.path.isdir(playlist_dir):
        print(f"Invalid directory: {playlist_dir}")
        sys.exit(1)

    # Ищем все .m3u и .m3u8 файлы в директории
    playlists = [f for f in os.listdir(playlist_dir) if f.lower().endswith(('.m3u', '.m3u8'))]
    if not playlists:
        print(f"No .m3u or .m3u8 files found in {playlist_dir}")
        sys.exit(0)

    print(f"Found {len(playlists)} playlists in {playlist_dir}. Processing...")

    # Путь к оригинальному скрипту (измените, если он в другом месте)
    import_script = 'import-m3u-to-spotify.py'  # Или полный путь, напр. r'C:\path\to\import-m3u-to-spotify.py'

    for playlist_file in playlists:
        full_path = os.path.join(playlist_dir, playlist_file)
        print(f"\nProcessing: {full_path}")

        # Формируем команду
        cmd = [sys.executable, import_script, '-f', full_path, '-u', spotify_username]
        if args.debug:
            cmd.append('-d')

        # Запускаем subprocess
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {full_path}: {e}")
        except FileNotFoundError:
            print(f"Original script not found: {import_script}")
            sys.exit(1)

    print("\nAll playlists processed.")