#!/usr/bin/env python3
"""
Teste: simular EXACTAMENTE o fluxo do scraper real (mobile + categorias via requests)
Usa o mesmo user-agent iPhone e o mesmo fluxo de carjet_requests.py
"""
import requests
import re
import time
import uuid
import sys

# Mesmo import que o scraper
from carjet_direct import parse_carjet_html_complete

UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']

def extract_redirect_url(html):
    patterns = [
        r"window\.location\.replace\('([^']+)'\)",
        r'window\.location\.replace\("([^"]+)"\)',
        r"window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]",
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    # Fallback
    m = re.search(r'/do/list/\w+\?[^"\'<>\s]*[sb]=[^"\'<>\s]+', html)
    if m:
        return m.group(0)
    return None

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': UA_IPHONE,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # PASSO 1: Homepage
    print("📱 PASSO 1: Homepage (mobile)...")
    resp_home = session.get('https://www.carjet.com/aluguel-carros/index.htm', timeout=15)
    print(f"   Status: {resp_home.status_code}, Cookies: {len(session.cookies)}")
    time.sleep(2)
    
    # PASSO 2: POST
    print("📱 PASSO 2: POST formulário...")
    form_data = {
        'frmDestino': 'FAO02',
        'frmDestinoFinal': '',
        'frmFechaRecogida': '10/02/2026 10:00',
        'frmFechaDevolucion': '24/02/2026 10:00',
        'frmHasAge': 'False',
        'frmEdad': '35',
        'frmPrvNo': '',
        'frmMoneda': 'EUR',
        'frmMonedaForzada': 'EUR',
        'frmJsonFilterInfo': '',
        'frmTipoVeh': 'CAR',
        'idioma': 'PT',
        'frmSession': str(uuid.uuid4()),
        'frmDetailCode': ''
    }
    
    resp_post = session.post('https://www.carjet.com/do/list/pt', data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://www.carjet.com',
                 'Referer': 'https://www.carjet.com/aluguel-carros/index.htm'},
        timeout=10, allow_redirects=True)
    print(f"   Status: {resp_post.status_code}, URL: {resp_post.url[:80]}")
    
    # PASSO 3: Redirect
    if '/do/list/' not in resp_post.url:
        redir = extract_redirect_url(resp_post.text)
        if redir:
            full_url = f'https://www.carjet.com{redir}' if not redir.startswith('http') else redir
        else:
            print("❌ Sem redirect")
            return
    else:
        full_url = resp_post.url
    print(f"   Redirect: {full_url[:80]}...")
    
    # PASSO 4: Polling
    print("📱 PASSO 4: Polling...")
    html_results = None
    for attempt in range(8):
        delay = [4, 5, 6, 7, 8, 9, 10, 12][attempt]
        print(f"   Tentativa {attempt+1}/8 ({delay}s)...", end=" ", flush=True)
        time.sleep(delay)
        resp = session.get(full_url, timeout=15)
        html = resp.text
        has_cars = 'class="carCardWeb"' in html or 'class="price pr-euros"' in html or 'class="carCardMob"' in html
        print(f"{len(html)} bytes, carros={has_cars}")
        if has_cars:
            html_results = html
            break
    
    if not html_results:
        print("❌ Timeout - sem resultados")
        return
    
    # Parse homepage
    cars_home = parse_carjet_html_complete(html_results)
    print(f"\n✅ Homepage mobile: {len(cars_home)} carros")
    
    # Verificar Jogger na homepage
    joggers_home = [c for c in cars_home if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
    print(f"   Dacia Jogger na homepage: {len(joggers_home)}")
    for j in joggers_home:
        print(f"      {j.get('car','?'):30s} | {j.get('supplier','?'):20s} | {j.get('price','?')}")
    
    # PASSO 5: Categorias
    s_match = re.search(r'[?&]s=([^&]+)', full_url)
    b_match = re.search(r'[?&]b=([^&]+)', full_url)
    
    if not s_match or not b_match:
        print("⚠️ Sem tokens s/b - não pode buscar categorias")
        return
    
    s_token = s_match.group(1)
    b_token = b_match.group(1)
    
    print(f"\n📱 PASSO 5: Categorias...")
    all_cats_cars = []
    
    for cat in CATEGORIES:
        filter_data = dict(form_data)
        filter_data['frmAgrp'] = cat
        filter_data['frmPrvNo'] = ''
        
        resp_cat = session.post(
            f"https://www.carjet.com/do/list/pt?s={s_token}&b={b_token}",
            data=filter_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://www.carjet.com', 'Referer': full_url},
            timeout=10, allow_redirects=True)
        
        cat_html = resp_cat.text
        has_cars = 'class="carCardWeb"' in cat_html or 'class="price pr-euros"' in cat_html or 'class="carCardMob"' in cat_html
        
        if has_cars and len(cat_html) > 10000:
            cat_cars = parse_carjet_html_complete(cat_html)
        else:
            time.sleep(3)
            resp2 = session.get(resp_cat.url, timeout=10)
            cat_html2 = resp2.text
            has_cars2 = 'class="carCardWeb"' in cat_html2 or 'class="price pr-euros"' in cat_html2 or 'class="carCardMob"' in cat_html2
            if has_cars2:
                cat_cars = parse_carjet_html_complete(cat_html2)
            else:
                cat_cars = []
        
        all_cats_cars.extend(cat_cars)
        
        # Contar Jogger nesta categoria
        joggers_cat = [c for c in cat_cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
        print(f"   {cat:6s}: {len(cat_cars):3d} carros | Jogger: {len(joggers_cat)}")
        
        time.sleep(1)
    
    # Deduplicação
    total_before = len(all_cats_cars)
    seen = set()
    unique = []
    for car in all_cats_cars:
        key = (
            (car.get('car') or car.get('car_name') or '').strip().lower(),
            (car.get('supplier') or '').strip().lower(),
            (car.get('price') or '').strip().lower()
        )
        if key not in seen and key[0]:
            seen.add(key)
            unique.append(car)
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTADO FINAL (mobile requests)")
    print(f"{'='*60}")
    print(f"   Categorias bruto: {total_before}")
    print(f"   Após deduplicação: {len(unique)}")
    print(f"   Duplicados removidos: {total_before - len(unique)}")
    
    # Jogger final
    joggers_final = [c for c in unique if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
    print(f"\n   Dacia Jogger (únicos): {len(joggers_final)}")
    for j in joggers_final:
        print(f"      {j.get('car','?'):30s} | {j.get('supplier','?'):20s} | {j.get('price','?')}")
    
    # Suppliers
    from collections import Counter
    sups = Counter(c.get('supplier', '?') for c in unique)
    print(f"\n   Suppliers:")
    for s, cnt in sups.most_common(15):
        print(f"      {s:25s}: {cnt}")

if __name__ == '__main__':
    main()
