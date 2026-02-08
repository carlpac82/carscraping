#!/usr/bin/env python3
"""
Teste específico: verificar se o parse via requests captura os 2 Dacia Jogger da Surprice
"""
import requests
import re
import time
from carjet_direct import parse_carjet_html_complete

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    s_token = re.search(r'[?&]s=([^&]+)', SESSION_URL).group(1)
    b_token = re.search(r'[?&]b=([^&]+)', SESSION_URL).group(1)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
    })
    
    # Obter cookies
    resp = session.get(SESSION_URL, timeout=15)
    time.sleep(2)
    
    # Buscar VANS
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
    
    # 1. Contar "Jogger" no HTML bruto
    jogger_count_html = cat_html.lower().count('jogger')
    print(f"'Jogger' no HTML bruto: {jogger_count_html} ocorrências")
    
    # 2. Contar "SUR" (Surprice) no HTML
    sur_count = cat_html.count('data-prv="SUR"')
    print(f"data-prv='SUR' no HTML: {sur_count}")
    
    # 3. Extrair todos os artigos com Jogger
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(cat_html, 'lxml')
    articles = soup.find_all('article')
    print(f"\nTotal artigos no HTML: {len(articles)}")
    
    jogger_articles = []
    for art in articles:
        text = art.get_text()
        if 'jogger' in text.lower():
            prv = art.get('data-prv', '?')
            # Preço
            price_spans = art.find_all('span', class_='price')
            prices = []
            for ps in price_spans:
                classes = ps.get('class', [])
                if 'pr-euros' in classes and 'day' not in ' '.join(classes):
                    prices.append(ps.get_text(strip=True))
            jogger_articles.append({
                'supplier': prv,
                'prices': prices,
                'text_preview': text[:200].replace('\n', ' ')
            })
    
    print(f"\nArtigos com 'Jogger': {len(jogger_articles)}")
    for i, ja in enumerate(jogger_articles, 1):
        print(f"   {i}. Supplier: {ja['supplier']} | Preços: {ja['prices']}")
    
    # 4. Parse completo
    print(f"\n{'='*60}")
    print("Parse completo (parse_carjet_html_complete):")
    cars = parse_carjet_html_complete(cat_html)
    
    jogger_parsed = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
    print(f"Dacia Jogger no parse: {len(jogger_parsed)}")
    for j in jogger_parsed:
        name = j.get('car') or j.get('car_name', '?')
        sup = j.get('supplier', '?')
        price = j.get('price', '?')
        print(f"   {name:30s} | {sup:25s} | {price}")
    
    # 5. Verificar Surprice especificamente
    surprice_parsed = [c for c in cars if 'sur' in (c.get('supplier') or '').lower() or 'surprice' in (c.get('supplier') or '').lower()]
    print(f"\nTodos os carros Surprice/SUR no parse: {len(surprice_parsed)}")
    for s in surprice_parsed:
        name = s.get('car') or s.get('car_name', '?')
        price = s.get('price', '?')
        print(f"   {name:30s} | {price}")


if __name__ == '__main__':
    main()
