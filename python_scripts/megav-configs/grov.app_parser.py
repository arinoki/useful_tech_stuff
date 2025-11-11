import requests
import json
import subprocess
import tempfile
import os
import re
from urllib.parse import urlparse, parse_qs

base_url = "https://megav.app/servers-api/configs?page={page}&per_page=20&country=MD"
page = 1
configs = []

def parse_vless_url(config_url):
    """Парсит vless:// URL в dict для sing-box."""
    if not config_url.startswith('vless://'):
        return None
    parsed = urlparse(config_url.replace('vless://', ''))
    if '@' not in parsed.path:
        return None
    uuid, rest = parsed.path.split('@', 1)
    host, port_str = rest.split(':', 1)
    port = int(port_str.split('?')[0])
    query = parse_qs(parsed.query)
    
    # Базовый sing-box outbound для VLESS+GRPC (адаптируй под params)
    sing_config = {
        "outbounds": [{
            "type": "vless",
            "server": host,
            "server_port": port,
            "uuid": uuid.strip(),
            "flow": query.get('flow', [''])[0] or '',
            "packet_encoding": query.get('packetEncoding', [''])[0] or '',
            "tls": {
                "enabled": query.get('security', ['none'])[0] != 'none',
                "insecure": True  # Для теста, но в проде false!
            },
            "transport": {
                "type": "grpc",
                "service_name": query.get('serviceName', [''])[0] or '',
                "idle_timeout": "30s",
                "permit_without_stream": True
            }
        }]
    }
    # Добавь другие params (mode=gun -> reality? Но для базового хватит)
    return sing_config

def test_vless_server(config_url, timeout=10):
    """Тестирует сервер через sing-box. Возвращает True если ок."""
    sing_config = parse_vless_url(config_url)
    if not sing_config:
        return False
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"log": {"level": "error"}, "outbounds": sing_config["outbounds"]}, f)
        config_path = f.name
    
    try:
        # Sing-box run с тестом (попытка connect к google.com через outbound)
        cmd = [
            'sing-box', 'run', '-c', config_path,
            '--test-url', 'https://www.google.com/generate_204'  # Простой тест
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        os.unlink(config_path)
        return result.returncode == 0 and 'error' not in result.stderr.lower()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        if os.path.exists(config_path):
            os.unlink(config_path)
        return False

# Основной цикл (без изменений, кроме фильтра)
while True:
    url = base_url.format(page=page)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка на странице {page}: статус {response.status_code}")
            break
        data = response.json()
        if data.get('configs') is None:
            print(f"Configs is null на странице {page}. Остановка.")
            break
        for config in data['configs']:
            if config['protocol'] == 'vless':
                config_url = config['config_url']
                if test_vless_server(config_url):
                    configs.append(config_url)
        print(f"Страница {page}: добавлено {len([c for c in data['configs'] if c['protocol'] == 'vless'])} VLESS-конфигов")
        page += 1
    except Exception as e:
        print(f"Ошибка на странице {page}: {e}")
        break

# Запись (как раньше)
with open('megav.app.txt', 'w', encoding='utf-8') as f:
    for config in configs:
        f.write(config + '\n')

print(f"Готово! Всего VLESS-конфигов: {len(configs)}. Сохранено в megav.app.txt")