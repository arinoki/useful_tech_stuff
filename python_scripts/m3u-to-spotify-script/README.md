# README.md

# Импорт M3U плейлистов в Spotify

Этот репозиторий содержит скрипты для импорта локальных M3U/M3U8 плейлистов в Spotify. Основной скрипт извлекает метаданные (теги) из аудиофайлов различных форматов (MP3, OGG, Opus, M4A, FLAC и другие), ищет соответствующие треки в Spotify и создаёт новый плейлист. Обёртка позволяет обрабатывать все плейлисты в указанной директории.

Поддержка форматов обеспечивается библиотекой **mutagen**, которая заменяет eyed3 для совместимости с не-MP3 файлами.

## Требования

- Python 3.6+.
- Зависимости: `pip install spotipy termcolor mutagen`.

## Настройка

1. **Spotify API credentials**:
   - Зарегистрируйтесь на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Создайте приложение и получите `CLIENT_ID` и `CLIENT_SECRET`.
   - Установите переменные окружения:
     - Windows (PowerShell): `setx SPOTIPY_CLIENT_ID "your-client-id"` и аналогично для `SPOTIPY_CLIENT_SECRET`.
     - Linux/Mac: `export SPOTIPY_CLIENT_ID="your-client-id"` и аналогично для `SPOTIPY_CLIENT_SECRET`.
   - `SPOTIPY_REDIRECT_URI` по умолчанию: `http://127.0.0.1:8888/callback` (можно переопределить).

2. **Скопируйте скрипты** в одну папку.

## Использование

### Основной скрипт: `import-m3u-to-spotify.py`

```bash
python import-m3u-to-spotify.py -f "path/to/playlist.m3u8" -u your-spotify-username [-d]
```

- `-f`: Путь к M3U файлу (обязательно).
- `-u`: Spotify username (обязательно).
- `-d`: Режим отладки (опционально, выводит логи о тегах и поиске).

Скрипт:
- Парсит M3U, ищет файлы относительно пути плейлиста или текущей директории.
- Читает теги (artist/title) из файлов.
- Если теги отсутствуют, угадывает из имени файла (по разделителю `-` или `_`).
- Ищет треки в Spotify (порог совпадения: 50%).
- Создаёт приватный плейлист с именем файла.

### Обёртка: `batch-import-m3u.py`

```bash
python batch-import-m3u.py [-u your-spotify-username] [-dir "path/to/playlists"] [-d]
```

- `-u`: Spotify username (интерактивно, если не указан).
- `-dir`: Директория с плейлистами (интерактивно, дефолт: `~/Desktop/playlists`).
- `-d`: Режим отладки для всех скриптов.

Обработка всех `.m3u`/`.m3u8` файлов в директории последовательно.

## Пример вывода

```
Logged-in As: Your Name (your-username)
Parsed 26 tracks from path/to/playlist.m3u8

'C:\path\to\song.opus'
Tag data: 'Artist' - 'Title'
Guess from filename: Not required
Spotify: 'Artist' - 'Title', spotify:track:id [green]

26/26 of tracks matched on Spotify, creating playlist "playlist.m3u8" on Spotify... done
```

## Ограничения

- Поиск по artist + title; если совпадений нет, трек пропускается.
- Плейлисты создаются приватными; лимит треков — 100 за раз (автоматическая разбивка).
- Только базовые теги (artist/title); альбомы/длительность не используются.

## Лицензия

Этот проект лицензирован под [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ru).  
Атрибуция: © Arinoki, 2025.  
Распространение только в неизменённом виде, без коммерческого использования.

---