import asyncio
import yt_dlp
import os
import re
import sys
import logging
from pathlib import Path
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
# Путь к файлу с кукисами. Используем Path для кроссплатформенности и удобства.
# Убедитесь, что этот путь верен.
COOKIES_FILE = Path("C:/Soft/!!python_scripts/cookies.txt")

# Максимальное количество одновременных загрузок
CONCURRENT_DOWNLOADS_LIMIT = 8 # Здесь вы можете изменить количество потоков

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Выводим логи в stdout
    ]
)

# --- Ваш YtDlpLogger класс должен быть здесь, как и раньше ---
class YtDlpLogger(logging.Logger):
  def debug(self, msg):
      # yt-dlp часто выводит много отладочной информации,
      # мы можем фильтровать ее или логировать только INFO/WARNING/ERROR
      # if msg.startswith('[debug]'):
      #     self.info(msg) # Или pass, если не хотим видеть debug
      pass # Если не хотите логировать дебаг сообщения yt-dlp

  def info(self, msg):
      # Перехватываем только важные сообщения yt-dlp
      if '[download]' in msg or '[ExtractAudio]' in msg or '[info]' in msg or '[Metadata]' in msg or '[EmbedThumbnail]' in msg:
          logger.info(msg)
      else:
          pass # Или logger.debug(msg) если хотите видеть все

  def warning(self, msg):
      logger.warning(msg)

  def error(self, msg):
      logger.error(msg)

# Инициализация вашего основного логгера, если она отличается от YtDlpLogger
logger = logging.getLogger(__name__)

async def get_playlist_info(url: str):
    """
    Извлекает название плейлиста и список кортежей (ID видео, индекс в плейлисте).
    """
    ydl_opts_info = {
        'extract_flat': True,       # Получаем только поверхностную информацию, без рекурсивной загрузки
        'force_generic_extractor': True, # Помогает с URL YouTube Music
        'quiet': True,              # Подавляем вывод yt-dlp, будем использовать наш логгер
        'no_warnings': True,        # Подавляем предупреждения yt-dlp, они пойдут через наш логгер
        'simulate': True,           # Только симулируем, ничего не скачиваем
        'format': 'bestaudio',      # Необходимо для некоторых экстракторов
        'cookiefile': str(COOKIES_FILE) if COOKIES_FILE.exists() else None,
        'cachedir': False,          # Отключаем кеширование
        'ignoreerrors': True,       # Игнорировать ошибки при извлечении информации
        'nocheckcertificate': True, # Игнорировать ошибки SSL
        'logger': YtDlpLogger(name='YtDlpLogger'),    # Используем наш кастомный логгер для yt-dlp
        'socket_timeout': 60,       # Таймаут для сетевых операций
        'use_extractors': ['youtube'],
        'force_ipv4': True,         # Принудительное использование IPv4
        'extractor_args': {
          'youtube': {
                'skip': ['translated_subs'],
            }
        },
    }

    playlist_title = "Unknown_Playlist"
    video_data = [] # Список кортежей (video_id, playlist_index)

    logger.info(f"Получение информации о плейлисте: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)

            if '_type' in info and info['_type'] == 'playlist':
                playlist_title = info.get('title', 'Unknown_Playlist')
                entries = info.get('entries', [])
            elif 'id' in info: # Это одиночное видео
                playlist_title = info.get('playlist_title') or info.get('uploader') or info.get('title', 'Unknown_Video')
                entries = [info]
            else:
                logger.warning("Не удалось определить тип URL или извлечь информацию.")
                return None, []

            # Process entries to get video IDs and indices
            for i, entry in enumerate(entries):
                if entry and entry.get('id'):
                    # Use playlist_index if available, otherwise use our own counter (1-based)
                    # For a single video, playlist_index will be None, so it will get i+1
                    index_to_use = entry.get('playlist_index') if entry.get('playlist_index') is not None else (i + 1)
                    video_data.append((entry['id'], index_to_use))

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Ошибка загрузки/извлечения информации о плейлисте: {e}")
        return None, []
    except yt_dlp.utils.ExtractorError as e:
        logger.error(f"Ошибка экстрактора при получении информации о плейлисте: {e}")
        return None, []
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении информации о плейлисте: {e}")
        return None, []

    sanitized_title = re.sub(r'[\\/:*?"<>|]', '', playlist_title).strip()
    if not sanitized_title:
        sanitized_title = f"Downloaded_Playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return sanitized_title, video_data

async def download_video(video_id: str, playlist_index: int | None, download_dir: Path, cookies_file_path: Path):
  """
  Скачивает одно видео, используя yt-dlp как библиотеку Python.
  """
  video_url = f"https://www.youtube.com/watch?v={video_id}"

  download_dir.mkdir(parents=True, exist_ok=True)

  # Шаблон имени файла. yt-dlp сам подставит правильное расширение (m4a)
  output_template = f"{playlist_index:03d}. %(uploader)s - %(title)s.%(ext)s" if playlist_index is not None else "%(uploader)s - %(title)s.%(ext)s"

  # --- НАЧАЛО ИСПРАВЛЕННЫХ ОТСТУПОВ И ИМЕНИ ---
  ydl_opts = {
      # Пытаемся найти лучший m4a поток. Если не находим, то ищем лучший аудиопоток в целом.
      'format': 'bestaudio[ext=m4a]/bestaudio/best',
      'extract_audio': True,           # <--- Включаем встроенное извлечение аудио yt-dlp
      'audioformat': 'm4a',            # <--- Указываем целевой формат как m4a
      'outtmpl': str(download_dir / output_template),
      'addmetadata': True,
      'embedthumbnail': True,
      'writethumbnail': True,          # yt-dlp сам удалит webp после встраивания
      'postprocessors': [
          {
              'key': 'EmbedThumbnail', # Встраиваем обложку
          },
          {
              'key': 'FFmpegMetadata', # Добавляем метаданные после всего
          }
      ],
      'ignoreerrors': True,
      'noplaylist': True,              # Обрабатывать как одиночное видео
      'quiet': False,
      'no_warnings': False,
      'cookiefile': str(cookies_file_path) if cookies_file_path.exists() else None,
      'cachedir': False,               # Отключаем кеширование
      'nocheckcertificate': True,
      'retries': 5,
      'fragment_retries': 5,
      'logger': YtDlpLogger(name='YtDlpLogger'), # Передаем экземпляр логгера
      'socket_timeout': 60,
      'use_extractors': ['youtube'],
      'force_ipv4': True,
      'extractor_args': {
          'youtube': {
              'skip': ['translated_subs'],
          }
      },
      'sponsorblock_remove': 'default', # <--- Добавляем SponsorBlock
  }

  logger.info(f"Начинается загрузка видео {video_id} (Индекс: {playlist_index}) через yt-dlp библиотеку...")

  try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl: # <--- ИЗМЕНИТЕ ЗДЕСЬ НА yt_dlp.YoutubeDL
          info_dict = await asyncio.to_thread(ydl.extract_info, video_url, download=True)
      logger.info(f"Видео {video_id} (Индекс: {playlist_index}) успешно загружено.")
      return True
  except Exception as e:
      logger.error(f"Ошибка загрузки видео {video_id} (Индекс: {playlist_index}): {e}")
      return False

async def main(playlist_url: str):
    """
    Основная асинхронная функция для обработки плейлиста.
    """
    playlist_name, video_data = await get_playlist_info(playlist_url)

    if not playlist_name or not video_data:
        logger.error("Не удалось обработать плейлист или он пуст. Завершение.")
        sys.exit(1)

    # Используем текущую рабочую директорию
    current_dir = Path.cwd() 
    download_dir = current_dir / playlist_name
    download_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Плейлист '{playlist_name}' будет загружен в: {download_dir}")
    logger.info(f"Найдено {len(video_data)} видео для загрузки.")

    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS_LIMIT)

    async def sem_task(video_id, playlist_index, download_dir, cookies_file_path):
        async with semaphore:
            await download_video(video_id, playlist_index, download_dir, cookies_file_path)

    tasks = [
        sem_task(video_id, p_index, download_dir, COOKIES_FILE)
        for video_id, p_index in video_data
    ]

    await asyncio.gather(*tasks)
    logger.info(f"Все загрузки завершены для плейлиста '{playlist_name}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Использование: python download_playlist.py <URL_плейлиста_или_видео>")
        sys.exit(1)

    playlist_url = sys.argv[1]

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main(playlist_url))
