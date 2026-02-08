#!/usr/bin/env python3
"""
Teste: fluxo COMPLETO do scraper (igual ao carjet_requests.py)
Verifica se captura os 2 Dacia Jogger da Surprice nas Minivans
"""
import requests
import re
import time
import uuid
from carjet_direct import parse_carjet_html_complete

def extract_redirect_url(html):
    patterns = [
        r"window\.location\.replace\('([^']+)'\)",
        r'window\.location\.replace\("([^"]+)"\)',
        r"window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]",
        r'/do/list/\w+\?[^"\'<>\s]*[sb]=[^"\'<>\s]+',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1) if '(' in p else m.group(0)
    return None

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    })
    
    # PASSO 1: Homepage
    print("📌 Passo 1: Homepage...")
    resp_home = session.get('https://www.carjet.com/aluguel-carros/index.htm', timeout=15)
    print(f"   Cookies: {len(session.cookies)}")
    time.sleep(2)
    
    # PASSO 2: POST
    print("📌 Passo 2: POST...")
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
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://www.carjet.com', 'Referer': 'https://www.carjet.com/aluguel-carros/index.htm'},
        timeout=10, allow_redirects=True)
    print(f"   Status: {resp_post.status_code}, URL: {resp_post.url[:80]}")
    
    # PASSO 3: Redirect
    if '/do/list/' not in resp_post.url:
        redir = extract_redirect_url(resp_post.text)
        full_url = f'https://www.carjet.com{redir}' if redir else None
    else:
        full_url = resp_post.url
    
    if not full_url:
        print("❌ Sem redirect URL")
        return
    print(f"   Redirect: {full_url[:80]}...")
    
    # PASSO 4: Polling
    print("📌 Passo 4: Polling...")
    html_results = None
    for attempt in range(8):
        delay = [4, 5, 6, 7, 8, 9, 10, 12][attempt]
        print(f"   Tentativa {attempt+1}/8 ({delay}s)...", end=" ", flush=True)
        time.sleep(delay)
        resp = session.get(full_url, timeout=15)
        html = resp.text
        has_cars = 'class="carCardWeb"' in html or 'class="price pr-euros"' in html
        print(f"{len(html)} bytes, carros={has_cars}")
        if has_cars:
            html_results = html
            break
    
    if not html_results:
        print("❌ Timeout")
        return
    
    # Parse homepage
    cars_home = parse_carjet_html_complete(html_results)
    print(f"\n✅ Homepage: {len(cars_home)} carros")
    
    # PASSO 5: Categorias (só VANS para este teste)
    s_match = re.search(r'[?&]s=([^&]+)', full_url)
    b_match = re.search(r'[?&]b=([^&]+)', full_url)
    
    if not s_match or not b_match:
        print("❌ Sem tokens s/b")
        return
    
    s_token = s_match.group(1)
    b_token = b_match.group(1)
    
    print(f"\n📌 Passo 5: Buscando VANS...")
    filter_data = dict(form_data)
    filter_data['frmAgrp'] = 'VANS'
    filter_data['frmPrvNo'] = ''
    
    resp_vans = session.post(
        f"https://www.carjet.com/do/list/pt?s={s_token}&b={b_token}",
        data=filter_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://www.carjet.com', 'Referer': full_url},
        timeout=10, allow_redirects=True)
    
    vans_html = resp_vans.text
    has_cars_vans = 'class="carCardWeb"' in vans_html or 'class="price pr-euros"' in vans_html
    print(f"   HTML: {len(vans_html)} bytes, carros={has_cars_vans}")
    
    if not has_cars_vans:
        print("   Polling...")
        time.sleep(3)
        resp_vans2 = session.get(resp_vans.url, timeout=10)
        vans_html = resp_vans2.text
        has_cars_vans = 'class="carCardWeb"' in vans_html or 'class="price pr-euros"' in vans_html
        print(f"   Polling: {len(vans_html)} bytes, carros={has_cars_vans}")
    
    if has_cars_vans:
        cars_vans = parse_carjet_html_complete(vans_html)
        print(f"   VANS: {len(cars_vans)} carros")
        
        # Procurar Jogger
        joggers = [c for c in cars_vans if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
        print(f"\n{'='*60}")
        print(f"🔍 DACIA JOGGER nas VANS: {len(joggers)}")
        print(f"{'='*60}")
        for j in joggers:
            name = j.get('car') or j.get('car_name', '?')
            sup = j.get('supplier', '?')
            price = j.get('price', '?')
            print(f"   {name:30s} | {sup:25s} | {price}")
        
        # Surprice especificamente
        surprice = [c for c in cars_vans if 'sur' in (c.get('supplier') or '').lower() or 'surprice' in (c.get('supplier') or '').lower()]
        print(f"\n   Todos Surprice: {len(surprice)}")
        for s in surprice:
            name = s.get('car') or s.get('car_name', '?')
            price = s.get('price', '?')
            print(f"   {name:30s} | {price}")
    else:
        print("   ❌ Sem carros nas VANS")
        # Verificar Jogger no HTML bruto
        jogger_in_html = vans_html.lower().count('jogger')
        print(f"   'Jogger' no HTML: {jogger_in_html}")

if __name__ == '__main__':
    main()
