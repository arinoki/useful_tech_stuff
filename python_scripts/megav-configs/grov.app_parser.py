import requests
import json

base_url = "https://megav.app/servers-api/configs?page={page}&per_page=20&country=MD"
page = 1
configs = []

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
                configs.append(config['config_url'])
        print(f"Страница {page}: добавлено {len([c for c in data['configs'] if c['protocol'] == 'vless'])} VLESS-конфигов")
        page += 1
    except Exception as e:
        print(f"Ошибка на странице {page}: {e}")
        break

# Запись в файл
with open('megav.app.txt', 'w', encoding='utf-8') as f:
    for config in configs:
        f.write(config + '\n')

print(f"Готово! Всего VLESS-конфигов: {len(configs)}. Сохранено в megav.app.txt")