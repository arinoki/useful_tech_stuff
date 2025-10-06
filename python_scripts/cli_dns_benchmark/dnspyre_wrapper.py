#!/usr/-bin/env python3
"""
Async wrapper for dnspyre — prints sorted by latency (mean in ms).
Usage examples:
  python dnspyre_wrapper.py        <-- Runs in interactive mode by default
  python dnspyre_wrapper.py --skip-interactive  <-- Skips interactive mode and uses default/cli args
  python dnspyre_wrapper.py --full --verbose-errors
  python dnspyre_wrapper.py --mode doh --concurrency 4
  python dnspyre_wrapper.py --domains google.com youtube.com
  python dnspyre_wrapper.py --repeats 5
"""
import argparse
import asyncio
import re
import shlex
import sys
from typing import Optional

# Default servers (можно добавить свои)
DOH_SERVERS = [
    "https://cloudflare-dns.com/dns-query", "https://xbox-dns.ru/dns-query",
    "https://dns.google/dns-query", "https://freedns.controld.com/p0",
    "https://dns.quad9.net/dns-query", "https://doh.opendns.com/dns-query",
    "https://dns.astracat.ru/dns-query", "https://dns.adguard-dns.com/dns-query",
    "https://dns.alidns.com/dns-query", "https://doh.cleanbrowsing.org/doh/family-filter/",
    "https://doh.dns.sb/dns-query", "https://dns.pub/dns-query",
    "https://dns.google/resolve", "https://dns.mullvad.net/dns-query",
    "https://base.dns.mullvad.net/dns-query", "https://dns.nextdns.io",
    "https://ada.openbld.net/dns-query", "https://zero.dns0.eu/",
    "https://doh.360.cn/dns-query", "https://private.canadianshield.cira.ca/dns-query",
    "https://dns.digitale-gesellschaft.ch/dns-query", "https://dns-doh.dnsforfamily.com/dns-query",
    "https://dnspub.restena.lu/dns-query", "https://public.dns.iij.jp/dns-query",
    "https://doh.libredns.gr/dns-query", "https://dns.switch.ch/dns-query",
    "https://doh.applied-privacy.net/query", "https://anycast.uncensoreddns.org/dns-query",
    "https://sky.rethinkdns.com/dns-query", "https://doh.flashstart.com/f17c9ee5",
]

DOT_SERVERS = [
    "1.1.1.1:853", "1.0.0.1:853", "9.9.9.9:853", "9.9.9.10:853", "8.8.8.8:853",
    "8.8.4.4:853", "xbox-dns.ru:853", "dns.google:853",
    "p0.freedns.controld.com:853", "dns.quad9.net:853", "dns.astracat.ru:853",
    "dns.adguard-dns.com:853", "family.adguard-dns.com:853",
    "unfiltered.adguard-dns.com:853",
    "family-filter-dns.cleanbrowsing.org:853",
    "adult-filter-dns.cleanbrowsing.org:853",
    "security-filter-dns.cleanbrowsing.org:853",
    "1dot1dot1dot1.cloudflare-dns.com:853", "security.cloudflare-dns.com:853",
    "family.cloudflare-dns.com:853", "dns10.quad9.net:853", "dns11.quad9.net:853",
    "dns.switch.ch:853", "dns.futuredns.me:853", "dns.comss.one:853",
    "dns.east.comss.one:853", "private.canadianshield.cira.ca:853",
    "protected.canadianshield.cira.ca:853", "dot-fi.blahdns.com:853",
    "dot-jp.blahdns.com:853", "dot-de.blahdns.com:853", "fi.dot.dns.snopyta.org:853",
    "dns-dot.dnsforfamily.com:853", "odvr.nic.cz:853", "dns.alidns.com:853",
    "dns.cfiec.net:853", "dot.360.cn:853", "public.dns.iij.jp:853",
    "dot.pub:853", "101.101.101.101:853", "dot.tiar.app:853", "jp.tiar.app:853",
    "dns.oszx.co:853", "dns.pumplex.com:853", "dot1.applied-privacy.net:853",
    "dns.decloudus.com:853", "resolver-eu.lelux.fi:853", "185.222.222.222:853",
    "dnsforge.de:853", "kaitain.restena.lu:853", "dot.ffmuc.net:853",
    "dns.digitale-gesellschaft.ch:853", "dot.libredns.gr:853",
    "ibksturm.synology.me:853", "getdnsapi.net:853", "dnsovertls.sinodun.com:853",
    "dnsovertls1.sinodun.com:853", "unicast.censurfridns.dk:853",
    "anycast.censurfridns.dk:853", "dns.cmrg.net:853", "dns.larsdebruin.net:853",
    "dns-tls.bitwiseshift.net:853", "ns1.dnsprivacy.at:853", "ns2.dnsprivacy.at:853",
    "dns.bitgeek.in:853", "dns.neutopia.org:853", "privacydns.go6lab.si:853",
    "dot.securedns.eu:853", "dot.nl.ahadns.net:853", "dot.in.ahadns.net:853",
    "dot.la.ahadns.net:853", "dot.ny.ahadns.net:853", "dot.pl.ahadns.net:853",
    "dot.it.ahadns.net:853", "dot.es.ahadns.net:853", "dot.no.ahadns.net:853",
    "dot.chi.ahadns.net:853", "dot.seby.io:853", "doh.dnslify.com:853",
    "dns.nextdns.io:853", "anycast.dns.nextdns.io:853", "max.rethinkdns.com:853",
    "p1.freedns.controld.com:853", "p2.freedns.controld.com:853",
    "p3.freedns.controld.com:853", "doh.mullvad.net:853",
    "adblock.doh.mullvad.net:853", "dandelionsprout.asuscomm.com:853",
]

PLAIN_DNS_SERVERS = [
    "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1", "9.9.9.9", "149.112.112.112",
    "208.67.222.222", "208.67.220.220", "8.26.56.26", "8.20.247.20",
    "94.140.14.14", "94.140.15.15", "77.88.8.8", "77.88.8.1", "1.1.1.2",
    "1.0.0.2", "1.1.1.3", "1.0.0.3", "9.9.9.10", "9.9.9.11", "64.6.64.6",
    "64.6.65.6", "223.5.5.5", "223.6.6.6", "185.228.168.9",
    "185.228.169.9", "195.46.39.39", "195.46.39.40", "216.146.35.35",
    "216.146.36.36", "74.82.42.42", "45.90.29.77", "149.112.112.11",
    "208.67.222.220", "8.26.56.10", "149.112.112.9",
]

DOQ_SERVERS = [
    "quic://dns.adguard-dns.com", "quic://dns.google", "quic://dns.nextdns.io",
    "quic://dns.quad9.net", "quic://dns.mullvad.net",
    "quic://family.adguard-dns.com", "quic://unfiltered.adguard-dns.com",
    "quic://dns.futuredns.me", "quic://doh.tiar.app", "quic://dns.comss.one",
    "quic://p0.freedns.controld.com", "quic://dandelionsprout.asuscomm.com:48582",
]

DOH3_SERVERS = [
    "https://dns.adguard-dns.com/dns-query",
    "https://dns.google/dns-query",
    "https://cloudflare-dns.com/dns-query",
    "https://dns.nextdns.io",
    "https://freedns.controld.com/p1",
    "https://dns.mullvad.net/dns-query",
    "https://basic.rethinkdns.com/dns-query",
    "https://doh-jp.blahdns.com/dns-query",
    "https://doh.tiarap.org/dns-query",
    "https://jp.tiarap.org/dns-query",
]


DEFAULT_DOMAINS = [
    "google.com", "youtube.com", "ya.ru", "yandex.ru", "github.com",
    "wikipedia.org", "amazon.com", "facebook.com", "microsoft.com",
    "twitter.com", "instagram.com", "linkedin.com", "netflix.com",
    "reddit.com", "tiktok.com", "vk.com", "mail.ru", "baidu.com",
    "taobao.com", "qq.com", "cloudflare.com", "akamai.com", "fastly.com",
    "example.com", "example.org", "example.net", "ipv6.google.com",
    "a.root-servers.net", "dnssec-failed.org", "nonexistent.invalid"
]

PAT_MEAN_MS = re.compile(r"\bmean[:\s=]*([\d.]+)\s*ms\b", re.IGNORECASE)
PAT_MEAN_S = re.compile(r"\bmean[:\s=]*([\d.]+)\s*s\b", re.IGNORECASE)
PAT_P50_MS = re.compile(r"\bp50[:\s=]*([\d.]+)\s*ms\b", re.IGNORECASE)
PAT_P50_S = re.compile(r"\bp50[:\s=]*([\d.]+)\s*s\b", re.IGNORECASE)
PAT_PNN_MS = re.compile(r"\bp\d{1,2}[:\s=]*([\d.]+)\s*ms\b", re.IGNORECASE)
PAT_PNN_S = re.compile(r"\bp\d{1,2}[:\s=]*([\d.]+)\s*s\b", re.IGNORECASE)
PAT_TIME_TAKEN_MS = re.compile(r"Time taken for tests[:\s]*([\d.]+)\s*ms\b", re.IGNORECASE)
PAT_TIME_TAKEN_S = re.compile(r"Time taken for tests[:\s]*([\d.]+)\s*s\b", re.IGNORECASE)
PAT_ANY_MS = re.compile(r"([\d.]+)\s*ms\b", re.IGNORECASE)
PAT_ANY_S = re.compile(r"([\d.]+)\s*s\b", re.IGNORECASE)

ANSI_ESC_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
BRACKET_TOKEN_RE = re.compile(r"\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    if not text:
        return text
    t = ANSI_ESC_RE.sub("", text)
    t = BRACKET_TOKEN_RE.sub("", t)
    return t

def parse_mean_ms(text: str) -> Optional[float]:
    if not text:
        return None
    t = strip_ansi(text)
    patterns = [
        (PAT_MEAN_MS, 1.0), (PAT_MEAN_S, 1000.0), (PAT_P50_MS, 1.0),
        (PAT_P50_S, 1000.0), (PAT_PNN_MS, 1.0), (PAT_PNN_S, 1000.0),
        (PAT_TIME_TAKEN_MS, 1.0), (PAT_TIME_TAKEN_S, 1000.0),
        (PAT_ANY_MS, 1.0), (PAT_ANY_S, 1000.0),
    ]
    for pat, multiplier in patterns:
        m = pat.search(t)
        if m:
            try:
                return float(m.group(1)) * multiplier
            except (ValueError, IndexError):
                continue
    return None

async def run_dnspyre(semaphore: asyncio.Semaphore, dnspyre_path: str, server: str, domains: list,
                      protocol: str, process_timeout: int, query_timeout: str, repeats: int):
    async with semaphore:
        cmd = [dnspyre_path]


        if protocol == "DoT":
            cmd.append("--dot")
        elif protocol == "DoH3":
            cmd.extend(["--doh-protocol", "3"])

        if query_timeout:
            cmd.extend(["--request", query_timeout])

        if repeats > 1:
            cmd.extend(["-n", str(repeats)])

        cmd.extend(["--server", server])
        cmd.extend(domains)

        start = asyncio.get_event_loop().time()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except FileNotFoundError:
            return {
                "server": server, "protocol": protocol, "success": False, "mean_ms": None,
                "wall_ms": None, "stderr": f"dnspyre not found ({dnspyre_path})",
                "cmd": " ".join(shlex.quote(p) for p in cmd), "returncode": None,
            }
        except Exception as e:
             return {
                "server": server, "protocol": protocol, "success": False, "mean_ms": None,
                "wall_ms": None, "stderr": f"Execution error: {e}",
                "cmd": " ".join(shlex.quote(p) for p in cmd), "returncode": None,
            }

        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=process_timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            wall = (asyncio.get_event_loop().time() - start) * 1000.0
            return {
                "server": server, "protocol": protocol, "success": False, "mean_ms": None,
                "wall_ms": wall, "stderr": f"Timeout after {process_timeout}s (Process killed)",
                "cmd": " ".join(shlex.quote(p) for p in cmd), "returncode": None,
            }
        wall = (asyncio.get_event_loop().time() - start) * 1000.0
        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")
        mean_ms = parse_mean_ms(stdout)
        success = (proc.returncode == 0)
        return {
            "server": server, "protocol": protocol, "success": success, "mean_ms": mean_ms,
            "wall_ms": wall, "stderr": stderr.strip(),
            "cmd": " ".join(shlex.quote(p) for p in cmd), "returncode": proc.returncode,
        }

async def run_all(args):
    semaphore = asyncio.Semaphore(args.concurrency)
    tasks = []
    # Если domains не задан через CLI, используем DEFAULT_DOMAINS
    domains = args.domains if args.domains else DEFAULT_DOMAINS

    # args.mode может быть списком (из CLI) или строкой/списком (из интерактивного режима)
    modes = args.mode if isinstance(args.mode, list) else [args.mode]
    # Если интерактивный режим выбрал 'all' или режим был 'all' из CLI
    run_all_protocols = "all" in modes

    protocol_map = {
        "doh": ("DoH", args.doh_list), "dot": ("DoT", args.dot_list),
        "plain": ("Plain", args.plain_list), "doq": ("DoQ", args.doq_list),
        "doh3": ("DoH3", args.doh3_list),
    }
    tested_protocols = []

    # Фильтрация серверов
    for mode, (proto_name, server_list) in protocol_map.items():
        if run_all_protocols or mode in modes:
            tested_protocols.append(proto_name)
            for s in server_list:
                tasks.append(run_dnspyre(
                    semaphore, args.dnspyre, s, domains, proto_name,
                    args.process_timeout, args.query_timeout, args.repeats
                ))

    if not tasks:
        print("No tasks to run. Check --mode.")
        return 1

    total_unique_servers = len(tasks)
    total_servers = len(tasks) // args.repeats // len(domains) if args.repeats * len(domains) > 0 else 0
    print(f"\n--- Starting {len(tasks)} server tests (Servers: {total_unique_servers}, Domains per test: {len(domains)}, Repeats: {args.repeats}) ---")


    results = await asyncio.gather(*tasks)

    def key_fn(r):
        if r["mean_ms"] is not None:
            return (0, r["mean_ms"])
        if r["wall_ms"] is not None:
            return (1, r["wall_ms"])
        return (2, float("inf"))
    results_sorted = sorted(results, key=key_fn)

    results_to_print = results_sorted
    if not args.full and len(results_sorted) > 50:
        print(f"--- Top 50 results (use --full to see all {len(results_sorted)}) ---")
        results_to_print = results_sorted[:50]

    err_header = "ERROR" if args.verbose_errors else "ERR (truncated)"
    header = f"{'#':>3}  {'PROTO':5}  {'SERVER':45}  {'MEAN(ms)':>10}  {'RESULT':6}"
    sep = "-" * (len(header) if args.verbose_errors else 118)
    print(sep)
    print(header)
    print(sep)
    for idx, r in enumerate(results_to_print, start=1):
        proto, server = r["protocol"], r["server"]
        lat = "N/A"
        if r["mean_ms"] is not None: lat = f"{r['mean_ms']:.2f}"
        elif r["wall_ms"] is not None: lat = f"{r['wall_ms']:.2f}*"

        serr = (r.get("stderr") or "").replace("\n", " ").strip()
        if not args.verbose_errors and len(serr) > 40:
            serr = serr[:37] + "..."

        print(f"{idx:>3}  {proto:5}  {server:45.45}  {lat:>10}")
    print(sep)
    total, succ = len(results), sum(1 for r in results if r["success"])
    print(f"Total: {total}, Success: {succ}, Fail: {total - succ}")
    print("Звездочка '*' означает fallback на wall-clock время процесса.")

    print("\n" + "--- Top 5 results per protocol ---")
    top_5_by_protocol = {}
    # Используем только успешные результаты с реальной измеренной задержкой
    successful_results = [r for r in results_sorted if r["success"] and r["mean_ms"] is not None]
    for r in successful_results:
        proto = r["protocol"]
        if proto not in top_5_by_protocol: top_5_by_protocol[proto] = []
        if len(top_5_by_protocol[proto]) < 5: top_5_by_protocol[proto].append(r)

    summary_header = f"{'PROTO':5}  {'MEAN(ms)':>10}  {'SERVER'}"
    summary_sep = "-" * 45
    print(summary_header)
    for proto in tested_protocols:
        print(summary_sep)
        if proto in top_5_by_protocol and top_5_by_protocol[proto]:
            for r in top_5_by_protocol[proto]:
                print(f"{proto:5}  {r['mean_ms']:>10.2f}  {r['server']}")
        else:
            print(f"{proto:5}  {'N/A':>10}  (No successful tests)")
    print(summary_sep)
    return 0

def get_input_or_default(prompt: str, default_value, type_cast=str, validator=None, custom_modes=None):
    """
    Получает ввод от пользователя. Если ввод пуст или некорректен,
    возвращает значение по умолчанию с сообщением об ошибке.
    """
    default_str = f"[{default_value}]" if not isinstance(default_value, list) else f"[{', '.join(default_value)}]"

    while True:
        user_input = input(f"   {prompt} {default_str}: ").strip()

        if not user_input:
            print(f"   ⚙️ Используется значение по умолчанию: {default_value}")
            return default_value

        if custom_modes == "modes":
            # Специальная обработка для режимов
            all_modes = ["doh", "dot", "plain", "doq", "doh3", "all"]
            modes_selected = [m.strip().lower() for m in user_input.split(',') if m.strip()]
            valid_modes = [m for m in modes_selected if m in all_modes]

            if len(valid_modes) != len(modes_selected) or not valid_modes:
                 print(f"   ⚠️ Ошибка: Некорректный выбор протокола. Доступные: {', '.join(all_modes)}. Используется по умолчанию: {', '.join(default_value)}")
                 return default_value

            print(f"   ✅ Выбрано: {', '.join(valid_modes)}")
            return valid_modes

        try:
            # Попытка преобразовать введенное значение
            value = type_cast(user_input)

            # Если есть дополнительная проверка (валидатор)
            if validator and not validator(value):
                raise ValueError("Validator failed")

            print(f"   ✅ Выбрано: {value}")
            return value
        except ValueError:
            print(f"   ⚠️ Ошибка: Неверный формат или значение. Используется по умолчанию: {default_value}")
            return default_value

def interactive_mode(default_args):
    """Интерактивный ввод параметров."""
    print("\n" + "="*50)
    print("      🚀 Dnspyre Wrapper: Режим интерактивного запуска")
    print("="*50)

    # Шаг 1: Выбор режима запуска
    print("\nВыберите режим запуска:")
    print("  1) Автоматический (Auto) - запустить со всеми параметрами по умолчанию.")
    print("  2) Настроить (Custom) - пошагово задать основные параметры.")

    choice = input("   Ваш выбор (1/2): ").strip()

    if choice == '1':
        print("\n--- Запуск в Автоматическом режиме (параметры по умолчанию)... ---")
        return default_args

    print("\n--- Режим Настройки Параметров ---")

    # 1. Режим (Протокол)
    print("\n1. Выберите режим(ы) для тестирования (DoH, DoT, Plain, DoQ, DoH3, All).")
    default_args.mode = get_input_or_default(
        "Протоколы (разделитель - запятая, напр. doh,dot)",
        default_args.mode,
        custom_modes="modes"
    )

    # 2. Параллелизм (Concurrency)
    print("\n2. Укажите число параллельных тестов (concurrency).")
    default_args.concurrency = get_input_or_default(
        "Параллелизм (целое число > 0)",
        default_args.concurrency,
        type_cast=int,
        validator=lambda x: x > 0
    )

    # 3. Число повторений (Repeats)
    print("\n3. Укажите число повторений каждого теста (repeats, флаг -n в dnspyre).")
    default_args.repeats = get_input_or_default(
        "Повторения (целое число >= 1)",
        default_args.repeats,
        type_cast=int,
        validator=lambda x: x >= 1
    )

    # 4. Таймаут запроса (Query Timeout)
    print("\n4. Укажите таймаут для каждого DNS-запроса (query-timeout, например, 1s, 500ms).")
    default_args.query_timeout = get_input_or_default(
        "Таймаут запроса (строка, напр. 1s)",
        default_args.query_timeout,
        type_cast=str # Строка, валидация по паттерну слишком сложна для простого интерактива
    )

    # 5. Таймаут процесса (Process Timeout)
    print("\n5. Укажите таймаут для всего процесса dnspyre в секундах (process-timeout).")
    default_args.process_timeout = get_input_or_default(
        "Таймаут процесса (целое число > 0, секунды)",
        default_args.process_timeout,
        type_cast=int,
        validator=lambda x: x > 0
    )

    print("\n--- Интерактивный режим завершен. Запуск тестов... ---")
    return default_args

def main():
    parser = argparse.ArgumentParser(description="dnspyre wrapper: run many servers and print sorted by mean latency.")
    parser.add_argument("--mode", nargs="+", choices=["doh", "dot", "plain", "doq", "doh3", "all"], default=["all"],
                        help="DNS protocol(s) to test. 'all' tests every protocol.")
    parser.add_argument("--domains", nargs="+", help="Домены для тестирования (по умолчанию набор популярных).")
    parser.add_argument("--concurrency", type=int, default=4, help="Number of concurrent tests.")
    parser.add_argument("--dnspyre", default="dnspyre", help="Path to dnspyre executable.")
    parser.add_argument("--process-timeout", type=int, default=60,
                        help="Timeout for the whole dnspyre process for one server.")
    parser.add_argument("--query-timeout", default="1000ms",
                        help="Timeout for each individual DNS query (e.g., '1s', '500ms'). Passed to dnspyre's --request flag.")
    parser.add_argument("--repeats", type=int, default=1,
                        help="Number of test repetitions per server (dnspyre's -n flag).")
    parser.add_argument("--full", action="store_true", help="Display full list of servers instead of top 50.")
    parser.add_argument("--verbose-errors", action="store_true", help="Show full error messages instead of truncating them.")

    # Новый флаг для пропуска интерактивного режима, если пользователь задал параметры через CLI
    parser.add_argument("--skip-interactive", action="store_true", 
                        help="Skip the default interactive mode and use CLI arguments or defaults.")
    args = parser.parse_args()

    args.doh_list, args.dot_list = DOH_SERVERS, DOT_SERVERS
    args.plain_list, args.doq_list = PLAIN_DNS_SERVERS, DOQ_SERVERS
    args.doh3_list = DOH3_SERVERS

    # Проверяем, нужно ли запускать интерактивный режим
    # Интерактивный режим пропускается, если есть флаг --skip-interactive ИЛИ если задан любой из ключевых параметров через CLI
    is_cli_configured = any(arg in sys.argv for arg in ["--mode", "--domains", "--concurrency", "--process-timeout", "--query-timeout", "--repeats"])

    if not args.skip_interactive and not is_cli_configured:
        args = interactive_mode(args)
    elif is_cli_configured:
         print("--- Обнаружены параметры CLI. Интерактивный режим пропущен. ---")


    try:
        rc = asyncio.run(run_all(args))
        raise SystemExit(rc)
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C).")
        raise SystemExit(1)
    except SystemExit:
        # Это для SystemExit из run_all
        pass
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
