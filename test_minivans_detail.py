#!/usr/bin/env python3
"""
Teste detalhado: ver TODOS os carros da categoria VANS (Minivans)
Para comparar com o que aparece no site CarJet
"""
import requests
import re
import time
from carjet_direct import parse_carjet_html_complete

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    s_match = re.search(r'[?&]s=([^&]+)', SESSION_URL)
    b_match = re.search(r'[?&]b=([^&]+)', SESSION_URL)
    s_token = s_match.group(1)
    b_token = b_match.group(1)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
    })
    
    # Obter cookies
    print("📌 Obtendo cookies...")
    resp = session.get(SESSION_URL, timeout=15)
    time.sleep(2)
    
    # Buscar VANS (Minivans)
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
    
    print("\n📂 Buscando VANS (Minivans)...")
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
    
    print(f"\n{'='*80}")
    print(f"🚐 MINIVANS: {len(cars)} carros encontrados pelo scraper")
    print(f"{'='*80}")
    
    # Mostrar TODOS os carros com detalhe
    for i, car in enumerate(cars, 1):
        name = car.get('car') or car.get('car_name', '?')
        supplier = car.get('supplier', '?')
        price = car.get('price', '?')
        transmission = car.get('transmission', '?')
        category = car.get('category', '?')
        grupo = car.get('grupo', car.get('group', '?'))
        
        print(f"   {i:2d}. {name:40s} | {supplier:25s} | {price:>12s} | {transmission:10s} | {grupo}")
    
    # Agrupar por nome de carro
    print(f"\n{'='*80}")
    print(f"📊 AGRUPADO POR CARRO")
    print(f"{'='*80}")
    
    from collections import defaultdict
    by_car = defaultdict(list)
    for car in cars:
        name = car.get('car') or car.get('car_name', '?')
        by_car[name].append(car)
    
    for car_name, entries in sorted(by_car.items()):
        print(f"\n   🚗 {car_name} ({len(entries)} ofertas):")
        for e in entries:
            supplier = e.get('supplier', '?')
            price = e.get('price', '?')
            grupo = e.get('grupo', e.get('group', '?'))
            print(f"      - {supplier:25s} | {price:>12s} | Grupo: {grupo}")
    
    # Comparar com o que o site mostra
    print(f"\n{'='*80}")
    print(f"🔍 COMPARAÇÃO COM SITE CARJET (Minivans)")
    print(f"{'='*80}")
    print(f"   Site mostra (do screenshot):")
    print(f"      - Dacia Jogger | Surprice  | 158,40€")
    print(f"      - Dacia Jogger | Surprice  | 180,02€ (Oferta Limitada)")
    print(f"      - Dacia Jogger | Thrifty   | 189,95€")
    print(f"      - Dacia Lodgy  | YesNo     | 192,47€")
    print(f"      - VW Sharan    | Europcar  | 369,60€")
    print(f"      - Peugeot 5008 | Greenmotion| 388,50€")
    print(f"      - ...e mais")
    
    print(f"\n   Scraper capturou:")
    # Procurar Dacia Jogger
    jogger_count = sum(1 for c in cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower())
    print(f"      - Dacia Jogger: {jogger_count} ofertas")
    for c in cars:
        if 'jogger' in (c.get('car') or c.get('car_name', '')).lower():
            print(f"        → {c.get('supplier', '?'):25s} | {c.get('price', '?'):>12s}")


if __name__ == '__main__':
    main()
