#!/usr/bin/env python3
"""
Teste: comparar resultados Minivans com user-agent iPhone vs Desktop
"""
import requests
import re
import time
from carjet_direct import parse_carjet_html_complete

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
UA_DESKTOP = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch_vans(user_agent, label):
    s_match = re.search(r'[?&]s=([^&]+)', SESSION_URL)
    b_match = re.search(r'[?&]b=([^&]+)', SESSION_URL)
    s_token = s_match.group(1)
    b_token = b_match.group(1)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
    })
    
    # Obter cookies
    resp = session.get(SESSION_URL, timeout=15)
    time.sleep(2)
    
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
        'frmSession': '',
        'frmDetailCode': '',
        'frmAgrp': 'VANS',
    }
    
    resp_cat = session.post(
        f"https://www.carjet.com/do/list/pt?s={s_token}&b={b_token}",
        data=form_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.carjet.com',
            'Referer': SESSION_URL,
        },
        timeout=10,
        allow_redirects=True
    )
    
    cat_html = resp_cat.text
    has_cars = 'class="carCardWeb"' in cat_html or 'class="price pr-euros"' in cat_html
    
    if has_cars and len(cat_html) > 10000:
        cars = parse_carjet_html_complete(cat_html)
    else:
        time.sleep(3)
        resp2 = session.get(resp_cat.url, timeout=10)
        cars = parse_carjet_html_complete(resp2.text)
    
    print(f"\n{'='*70}")
    print(f"📱 {label}: {len(cars)} carros")
    print(f"{'='*70}")
    
    for i, car in enumerate(cars, 1):
        name = car.get('car') or car.get('car_name', '?')
        supplier = car.get('supplier', '?')
        price = car.get('price', '?')
        grupo = car.get('grupo', car.get('group', '?'))
        print(f"   {i:2d}. {name:40s} | {supplier:25s} | {price:>12s} | {grupo}")
    
    # Verificar Dacia Jogger
    jogger = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
    lodgy = [c for c in cars if 'lodgy' in (c.get('car') or c.get('car_name', '')).lower()]
    sharan = [c for c in cars if 'sharan' in (c.get('car') or c.get('car_name', '')).lower()]
    
    print(f"\n   Dacia Jogger: {len(jogger)}")
    print(f"   Dacia Lodgy: {len(lodgy)}")
    print(f"   VW Sharan: {len(sharan)}")
    
    # Verificar se HTML tem "Jogger" em texto
    has_jogger_html = 'Jogger' in cat_html or 'jogger' in cat_html.lower()
    print(f"   'Jogger' no HTML: {has_jogger_html}")
    
    # Contar artigos no HTML
    import re as re2
    articles = re2.findall(r'<article', cat_html)
    print(f"   <article> tags no HTML: {len(articles)}")
    
    # Verificar se é versão mobile
    is_mobile = 'carCardMob' in cat_html
    is_desktop = 'carCardWeb' in cat_html
    print(f"   carCardMob: {is_mobile} | carCardWeb: {is_desktop}")
    
    return cars

print("🔍 TESTE: iPhone vs Desktop para Minivans")
print("="*70)

cars_iphone = fetch_vans(UA_IPHONE, "iPhone (user-agent do scraper)")
time.sleep(2)
cars_desktop = fetch_vans(UA_DESKTOP, "Desktop (user-agent do browser)")
