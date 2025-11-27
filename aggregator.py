# The original version was taken from https://github.com/y9felix/s

import urllib.request
import concurrent.futures
import json
import os
import re
import requests

def fetch_single_url(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode(errors='ignore').splitlines()
    except Exception:
        return []

def get_flag(code):
    return ''.join(chr(ord(c) + 127397) for c in code.upper()) if code else ''

def get_country_batch(ip_list):
    url = "http://ip-api.com/batch?fields=countryCode,query"
    try:
        data = json.dumps(ip_list)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json()
            return {item['query']: item.get('countryCode', '') for item in results}
    except Exception as e:
        print(f"Ошибка GeoIP API: {e}")
    return {}

def get_aggregated_links(url_map, selected_categories, keywords, use_old=False, log_func=print):
    urls = []
    old_lines = set()
    unique_configs = set()
    
    PROTOCOL_PATTERN = re.compile(r'^(vless|vmess|trojan|ss|hysteria2|hy2)://', re.IGNORECASE)
    IP_EXTRACT_PATTERN = re.compile(r'@([^:]+):')

    if use_old and os.path.exists('old.json'):
        try:
            with open('old.json', 'r') as f:
                old_lines = set(json.load(f))
        except: pass

    for cat in selected_categories:
        sources = url_map.get(cat, [])
        if isinstance(sources, list):
            urls.extend(sources)
        elif isinstance(sources, str):
            urls.extend(sources.split())

    log_func(f"АГРЕГАТОР: Загрузка из {len(urls)} источников...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        for result in executor.map(fetch_single_url, urls):
            for line in result:
                cleaned = line.split('#')[0].strip()
                
                if not cleaned: continue
                if not PROTOCOL_PATTERN.match(cleaned): continue
                
                is_valid = True
                if keywords:
                    is_valid = any(word.lower() in line.lower() for word in keywords)
                
                if is_valid and cleaned not in old_lines:
                    unique_configs.add(cleaned)

    config_list = list(unique_configs)
    total_configs = len(config_list)

    if total_configs > 0:
        log_func(f"АГРЕГАТОР: Найдено {total_configs} конфигов. Определение стран...")
        
        ips_to_resolve = []
        for line in config_list:
            match = IP_EXTRACT_PATTERN.search(line)
            if match:
                ips_to_resolve.append(match.group(1))
        
        ips_to_resolve = list(set(ips_to_resolve))
        
        ip_country_map = {}
        batch_size = 100
        
        for i in range(0, len(ips_to_resolve), batch_size):
            batch_ips = ips_to_resolve[i:i + batch_size]
            log_func(f"GeoIP Batch {i // batch_size + 1}/{(len(ips_to_resolve)-1)//batch_size + 1}")
            batch_results = get_country_batch(batch_ips)
            ip_country_map.update(batch_results)
            
        final_lines = []
        for line in config_list:
            match = IP_EXTRACT_PATTERN.search(line)
            ip = match.group(1) if match else ''
            
            country_code = ip_country_map.get(ip, '')
            flag = get_flag(country_code)
            
            if flag:

                final_lines.append(f"{line} {flag}" if '#' in line else f"{line}#{flag}")
            else:
                final_lines.append(line)
                
        log_func(f"АГРЕГАТОР: Собрано {len(final_lines)} новых уникальных конфигураций с флагами.")
        return final_lines

    log_func("АГРЕГАТОР: Ничего нового не найдено.")
    return []

# +═════════════════════════════════════════════════════════════════════════+
# ║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
# ║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
# ║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
# ║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
# ║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
# ║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
# ║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
# ║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
# ║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
# ║                                                                         ║
# +═════════════════════════════════════════════════════════════════════════+
# ║                               by MKultra69                              ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                      https://github.com/MKultra6969                     ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                  mk69.su                                ║
# +═════════════════════════════════════════════════════════════════════════+