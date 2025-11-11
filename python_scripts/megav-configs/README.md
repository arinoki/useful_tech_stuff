# Megav Configs

[English version](README_en.md)

## Описание
Этот репозиторий автоматически обновляет список VLESS-конфигов серверов из [megav.app](https://megav.app) (страна: MD). Скрипт парсит API, фильтрует только VLESS и сохраняет в [megav.app.txt](megav-configs/megav.app.txt) — один сервер на строку в формате `vless://...`.

Обновление происходит **раз в час** через GitHub Actions. Файл всегда актуальный!

## Как использовать
1. Скачай [megav.app.txt](megav-configs/megav.app.txt).
2. Импортируй строки в свой VLESS-клиент (например, v2rayNG, Nekobox).
3. Для ручного обновления: Запусти [update_configs.py](megav-configs/update_configs.py) локально или триггерь workflow в GitHub Actions.

## Структура
- `python_scripts/megav-configs/update_configs.py` — скрипт для парсинга.
- `python_scripts/megav-configs/megav.app.txt` — актуальные конфиги.
- `.github/workflows/update.yml` — автоматизация.

Если нужно доработать — пиши в Issues!

---
*Автоматическое обновление: [Actions](https://github.com/твой-username/твой-репозиторий/actions/workflows/update.yml)*