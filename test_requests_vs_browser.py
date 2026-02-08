#!/usr/bin/env python3
"""
Simular EXACTAMENTE o que o Railway faz via requests para a categoria VANS
e comparar com o que o browser mostra (73 artigos, 16 Jogger)
"""
import requests
import re
from bs4 import BeautifulSoup

UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

# Sessão do HTML colado pelo user
S_TOKEN = "56bed9eb-1d31-4a64-933c-e3d13428f2e8"
B_TOKEN = "15362c64-66d7-4cb3-84bf-9661ce12feaa"
FULL_URL = f"https://www.carjet.com/do/list/pt?s={S_TOKEN}&b={B_TOKEN}"

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': UA_IPHONE,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
    })
    
    # Primeiro visitar a URL para estabelecer sessão
    print("📌 Visitando URL principal...")
    resp = session.get(FULL_URL, timeout=15)
    print(f"   Status: {resp.status_code}, HTML: {len(resp.text)} bytes")
    
    homepage_html = resp.text
    articles_home = homepage_html.count('<article')
    jogger_home = homepage_html.lower().count('jogger')
    has_web = 'carCardWeb' in homepage_html
    has_mob = 'carCardMob' in homepage_html
    print(f"   Homepage: <article>={articles_home}, 'jogger'={jogger_home}, desktop={has_web}, mobile={has_mob}")
    
    # Form data exactamente como o scraper
    form_data = {
        'frmDestino': 'FAO02',
        'frmDestinoFinal': '',
        'frmFechaRecogida': '10/02/2026',
        'frmFechaDevolucion': '24/02/2026',
        'frmHasAge': 'False',
        'frmEdad': '35',
        'frmPrvNo': '',
        'frmMoneda': 'EUR',
        'frmMonedaForzada': 'EUR',
        'frmJsonFilterInfo': '',
        'frmTrans': 'none',
        'frmTipoVeh': 'CAR',
        'idioma': 'PT',
        'frmSession': '',
        'frmDetailCode': '',
        'frmAgrp': 'VANS',
    }
    
    filter_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.carjet.com',
        'Referer': FULL_URL,
    }
    
    # POST para VANS
    print(f"\n🚐 POST para VANS...")
    resp_vans = session.post(
        f"https://www.carjet.com/do/list/pt?s={S_TOKEN}&b={B_TOKEN}",
        data=form_data,
        headers=filter_headers,
        timeout=15,
        allow_redirects=True
    )
    
    vans_html = resp_vans.text
    articles_vans = vans_html.count('<article')
    jogger_vans = vans_html.lower().count('jogger')
    has_web_v = 'carCardWeb' in vans_html
    has_mob_v = 'carCardMob' in vans_html
    print(f"   VANS: {len(vans_html)} bytes, <article>={articles_vans}, 'jogger'={jogger_vans}, desktop={has_web_v}, mobile={has_mob_v}")
    
    # Salvar HTML
    with open('carjet_vans_requests.html', 'w', encoding='utf-8') as f:
        f.write(vans_html)
    
    # Parse
    from carjet_direct import parse_carjet_html_complete
    cars = parse_carjet_html_complete(vans_html)
    print(f"   Parsed: {len(cars)} carros")
    
    # Jogger
    jogger = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name') or '').lower()]
    print(f"   Jogger: {len(jogger)}")
    for j in jogger:
        print(f"      {j.get('car_name','?'):30s} | {j.get('supplier','?'):25s} | {j.get('price','?')}")
    
    # Todos os suppliers
    suppliers = set(c.get('supplier', '?') for c in cars)
    print(f"\n   Suppliers ({len(suppliers)}): {sorted(suppliers)}")
    
    # Comparar: quais suppliers faltam vs browser (que tem 16 Jogger)
    browser_jogger_suppliers = ['Surprice', 'Surprice', 'Auto Prudente Rent a Car', 'CarJet', 'Interrent', 
                                 'Kass Wagen', 'CarJet', 'Dollar', 'Dollar', 'Thrifty', 
                                 'Hertz', 'CarJet', 'Europcar', 'CarJet', 'CarJet', 'CarJet']
    requests_jogger_suppliers = [j.get('supplier', '?') for j in jogger]
    
    missing = []
    browser_copy = list(browser_jogger_suppliers)
    for s in requests_jogger_suppliers:
        if s in browser_copy:
            browser_copy.remove(s)
    
    if browser_copy:
        print(f"\n   ⚠️ JOGGER EM FALTA no requests: {browser_copy}")
    else:
        print(f"\n   ✅ Todos os Jogger capturados!")

if __name__ == '__main__':
    main()
