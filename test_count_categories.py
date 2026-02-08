#!/usr/bin/env python3
"""
Teste rápido: conta carros por categoria usando requests (mesmo método do scraper)
Usa a sessão CarJet existente para verificar quantos carros são extraídos.
"""
import requests
import re
import time
import sys
from collections import defaultdict

# Importar parse do carjet_direct.py
from carjet_direct import parse_carjet_html_complete

CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']

# Sessão CarJet do utilizador (14 dias, Faro, 10 Fev)
SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    # Extrair tokens
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
    
    # Primeiro, visitar a página para obter cookies
    print("📌 Obtendo cookies da sessão...")
    resp = session.get(SESSION_URL, timeout=15)
    print(f"   Status: {resp.status_code}, HTML: {len(resp.text)} bytes")
    time.sleep(2)
    
    # Form data base (mesmo que o scraper usa)
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
        'frmDetailCode': ''
    }
    
    all_cars = []
    cars_by_category = {}
    suppliers_by_category = {}
    
    print(f"\n{'='*70}")
    print(f"🚗 TESTE: SCRAPER COM CATEGORIAS (requests)")
    print(f"{'='*70}")
    
    for cat_code in CATEGORIES:
        print(f"\n   📂 {cat_code}...", end=" ", flush=True)
        
        try:
            filter_data = dict(form_data)
            filter_data['frmAgrp'] = cat_code
            filter_data['frmPrvNo'] = ''
            
            resp_cat = session.post(
                f"https://www.carjet.com/do/list/pt?s={s_token}&b={b_token}",
                data=filter_data,
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
                cat_cars = parse_carjet_html_complete(cat_html)
            else:
                time.sleep(3)
                resp_cat2 = session.get(resp_cat.url, timeout=10)
                cat_html2 = resp_cat2.text
                has_cars2 = 'class="carCardWeb"' in cat_html2 or 'class="price pr-euros"' in cat_html2
                if has_cars2:
                    cat_cars = parse_carjet_html_complete(cat_html2)
                else:
                    cat_cars = []
            
            cars_by_category[cat_code] = cat_cars
            all_cars.extend(cat_cars)
            
            # Contar por supplier
            sup_counts = defaultdict(int)
            for car in cat_cars:
                sup = car.get('supplier', '?')
                sup_counts[sup] += 1
            suppliers_by_category[cat_code] = dict(sup_counts)
            
            top_sups = ", ".join(f"{s}:{c}" for s, c in sorted(sup_counts.items(), key=lambda x: -x[1])[:5])
            print(f"{len(cat_cars)} carros ({top_sups})")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ {e}")
            cars_by_category[cat_code] = []
    
    # Deduplicação (mesmo método do scraper)
    print(f"\n{'='*70}")
    print(f"🔄 DEDUPLICAÇÃO")
    print(f"{'='*70}")
    
    total_before = len(all_cars)
    seen = set()
    unique_cars = []
    for car in all_cars:
        key = (
            (car.get('car') or car.get('car_name') or '').strip().lower(),
            (car.get('supplier') or '').strip().lower(),
            (car.get('price') or '').strip().lower()
        )
        if key not in seen and key[0]:
            seen.add(key)
            unique_cars.append(car)
    
    print(f"   Total bruto: {total_before} carros (com duplicados entre categorias)")
    print(f"   Total único: {len(unique_cars)} carros (após deduplicação por nome+supplier+preço)")
    print(f"   Duplicados removidos: {total_before - len(unique_cars)}")
    
    # Resumo por supplier (únicos)
    print(f"\n{'='*70}")
    print(f"📊 CARROS ÚNICOS POR SUPPLIER")
    print(f"{'='*70}")
    
    sup_total = defaultdict(int)
    for car in unique_cars:
        sup = car.get('supplier', '?')
        sup_total[sup] += 1
    
    for sup, cnt in sorted(sup_total.items(), key=lambda x: -x[1]):
        bar = '█' * min(cnt, 30)
        print(f"   {sup:12s}: {cnt:3d} {bar}")
    
    print(f"\n   TOTAL: {len(unique_cars)} carros únicos de {len(sup_total)} suppliers")
    
    # Contar automáticos
    auto_count = sum(1 for car in unique_cars if car.get('transmission', '').lower() in ('automatic', 'automático'))
    manual_count = len(unique_cars) - auto_count
    print(f"   Automáticos: {auto_count} | Manuais: {manual_count}")
    
    # Resumo por categoria
    print(f"\n{'='*70}")
    print(f"📂 POR CATEGORIA")
    print(f"{'='*70}")
    for cat, cars in cars_by_category.items():
        print(f"   {cat:6s}: {len(cars):3d} carros")


if __name__ == '__main__':
    main()
