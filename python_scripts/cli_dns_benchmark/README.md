# dnspyre-wrapper-test

An asynchronous Python wrapper script designed to test the latency and reliability of numerous DNS servers (DoH, DoT, DoQ, DoH3, and Plain DNS) using the `dnspyre` tool. It provides a default interactive mode for easy configuration and sorts results by mean latency.

## 🚀 Features

* **Asynchronous Testing:** Efficiently tests hundreds of DNS servers in parallel.
* **Protocol Support:** Supports **DoH**, **DoT**, **DoQ**, **DoH3**, and **Plain DNS**.
* **Interactive Mode (Default):** Easy command-line interface to set key parameters (Protocol, Concurrency, Repeats, Timeouts).
* **Auto Mode:** Quickly run tests using all default settings.
* **Latency Ranking:** Outputs a clean, sorted table of results based on mean response time.
* **Built-in Server List:** Includes a comprehensive list of known public DNS resolvers for all supported protocols.

## ⚙️ Requirements

1.  **Python 3.7+**
2.  **`dnspyre` tool:** The script requires the **Go-utility** `dnspyre` to be installed and accessible in your system's PATH.

    You can find detailed installation instructions on the official homepage: **https://tantalor93.github.io/dnspyre/**.

    The easiest way is typically to download a pre-compiled binary from the releases page for your OS and add it to your PATH. Alternatively, if you have Go installed:
    
    ```bash
    # Install using go
    go install [github.com/tantalor93/dnspyre@latest](https://github.com/tantalor93/dnspyre@latest)
    ```

## 📝 Usage

The script runs in an interactive configuration mode by default.

### Default Interactive Run

Simply run the script. You will be prompted to choose between **Auto Mode** (default settings) and **Custom Mode**.

```bash
python dnspyre_wrapper.py
````

### Command Line Arguments (Skip Interactive Mode)

If you pass any key parameter via the command line, or use the `--skip-interactive` flag, the interactive setup will be skipped.

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--mode` | string/list | `all` | DNS protocol(s) to test: `doh`, `dot`, `plain`, `doq`, `doh3`, `all`. |
| `--domains` | list | (Default List) | Space-separated list of domains to query (e.g., `google.com ya.ru`). |
| `--concurrency` | int | `4` | Maximum number of **simultaneous server tests** to run at once. |
| `--repeats` | int | `1` | Number of test repetitions per server (maps to `dnspyre -n`). |
| `--query-timeout` | string | `1000ms` | Timeout for each individual DNS query (e.g., `1s`). |
| `--process-timeout` | int | `60` | Timeout in seconds for the entire `dnspyre` process for one server. |
| `--full` | flag | | Display **all** results, not just the top 50. |
| `--verbose-errors` | flag | | Show full error messages (stderr). |
| `--skip-interactive`| flag | | Skip the interactive menu and use CLI/defaults. |

**Example using CLI:**

```bash
# Test only DoH and DoT protocols, with 5 repeats and 8 parallel servers
python dnspyre_wrapper.py --mode doh dot --repeats 5 --concurrency 8
```

-----

# 🇷🇺 dnspyre-wrapper-test

Асинхронный Python-скрипт-обертка, предназначенный для тестирования задержки и надежности большого количества DNS-серверов (DoH, DoT, DoQ, DoH3 и Plain DNS) с использованием инструмента `dnspyre`. Скрипт предоставляет интерактивный режим для простой настройки и сортирует результаты по среднему значению задержки.

## 🚀 Возможности

  * **Асинхронное тестирование:** Эффективно тестирует сотни DNS-серверов параллельно.
  * **Поддержка протоколов:** Поддерживает **DoH**, **DoT**, **DoQ**, **DoH3** и **Plain DNS**.
  * **Интерактивный режим (по умолчанию):** Удобный интерфейс командной строки для установки ключевых параметров (Протокол, Параллелизм, Повторения, Таймауты).
  * **Автоматический режим:** Быстрый запуск тестов со всеми настройками по умолчанию.
  * **Ранжирование по задержке:** Выводит чистую, отсортированную таблицу результатов на основе среднего времени ответа.
  * **Встроенный список серверов:** Включает обширный список известных публичных DNS-резолверов для всех поддерживаемых протоколов.

## ⚙️ Требования

1.  **Python 3.7+**

2.  **Инструмент `dnspyre`:** Скрипту требуется, чтобы **Go-утилита** `dnspyre` была установлена и доступна в переменной окружения PATH.

    Подробные инструкции по установке вы найдете на официальной домашней странице: **https://tantalor93.github.io/dnspyre/**.

    Самый простой способ — загрузить предварительно скомпилированный бинарный файл для вашей ОС со страницы релизов и добавить его в PATH. Если у вас установлен Go:

    ```bash
    # Установка с помощью go
    go install [github.com/tantalor93/dnspyre@latest](https://github.com/tantalor93/dnspyre@latest)
    ```

## 📝 Использование

Скрипт по умолчанию запускается в интерактивном режиме настройки.

### Запуск по умолчанию (Интерактивный режим)

Просто запустите скрипт. Вам будет предложено выбрать между **Автоматическим режимом** (настройки по умолчанию) и **Режимом настройки**.

```bash
python dnspyre_wrapper.py
```

### Аргументы командной строки (Пропуск Интерактивного режима)

Если вы передадите любой из ключевых параметров через командную строку, или используете флаг `--skip-interactive`, интерактивная настройка будет пропущена.

| Аргумент | Тип | По умолчанию | Описание |
| :--- | :--- | :--- | :--- |
| `--mode` | строка/список | `all` | Протокол(ы) DNS для тестирования: `doh`, `dot`, `plain`, `doq`, `doh3`, `all`. |
| `--domains` | список | (Список по умолчанию) | Список доменов для запроса через пробел (напр., `google.com ya.ru`). |
| `--concurrency` | целое | `4` | Максимальное количество **одновременных тестов серверов**. |
| `--repeats` | целое | `1` | Число повторений теста для каждого сервера (флаг `dnspyre -n`). |
| `--query-timeout` | строка | `1000ms` | Таймаут для каждого отдельного DNS-запроса (напр., `1s`). |
| `--process-timeout` | целое | `60` | Таймаут в секундах для всего процесса `dnspyre` для одного сервера. |
| `--full` | флаг | | Отобразить **все** результаты, а не только топ-50. |
| `--verbose-errors` | флаг | | Отображать полные сообщения об ошибках (stderr). |
| `--skip-interactive`| флаг | | Пропустить интерактивное меню и использовать аргументы CLI/по умолчанию. |

**Пример использования CLI:**

```bash
# Тестирование только протоколов DoH и DoT, с 5 повторениями и 8 параллельными серверами
python dnspyre_wrapper.py --mode doh dot --repeats 5 --concurrency 8
```
