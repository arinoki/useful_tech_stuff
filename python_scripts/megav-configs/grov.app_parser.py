import requests
import json

base_url = "https://megav.app/servers-api/configs?page={page}&per_page=20"
page = 1
configs = {}  # {host:port: config_url} для уникальности

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
        
        page_candidates = 0
        page_working = 0
        for config in data['configs']:
            if config['protocol'] == 'vless' and config['v2ray_status'] == 'working':
                page_candidates += 1
                host_port = f"{config['address']}:{config['port']}"
                if host_port not in configs:
                    configs[host_port] = config['config_url']
                    page_working += 1
        
        print(f"Страница {page}: {page_candidates} кандидатов, {page_working} новых уникальных working VLESS")
        page += 1
    except Exception as e:
        print(f"Ошибка на странице {page}: {e}")
        break

# Запись в файл (только уникальные)
with open('megav.app.txt', 'w', encoding='utf-8') as f:
    for config_url in configs.values():
        f.write(config_url + '\n')

print(f"Готово! Всего уникальных working VLESS: {len(configs)}. Сохранено в megav.app.txt")