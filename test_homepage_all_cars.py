#!/usr/bin/env python3
"""
Teste: verificar se o HTML da homepage (após polling) já contém TODOS os carros
incluindo os que só aparecem nas categorias no browser.
"""
import requests
import re
import time
import uuid
from carjet_direct import parse_carjet_html_complete

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-PT,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    })
    
    # PASSO 1: Homepage para cookies
    print("📌 Passo 1: Homepage...")
    home_url = 'https://www.carjet.com/aluguel-carros/index.htm'
    resp_home = session.get(home_url, timeout=15)
    print(f"   Status: {resp_home.status_code}, Cookies: {len(session.cookies)}")
    time.sleep(2)
    
    # PASSO 2: POST formulário
    print("📌 Passo 2: POST formulário...")
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
    
    resp_post = session.post(
        'https://www.carjet.com/do/list/pt',
        data=form_data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.carjet.com',
            'Referer': home_url,
        },
        timeout=10,
        allow_redirects=True
    )
    print(f"   Status: {resp_post.status_code}, URL: {resp_post.url[:80]}")
    
    # PASSO 3: Extrair redirect URL
    redirect_url = resp_post.url
    if '/do/list/' not in redirect_url:
        pattern = r"window\.location\.replace\('([^']+)'\)"
        match = re.search(pattern, resp_post.text)
        if match:
            redirect_url = f'https://www.carjet.com{match.group(1)}'
    
    print(f"   Redirect: {redirect_url[:80]}...")
    
    # PASSO 4: POLLING
    print("\n📌 Passo 4: Polling...")
    html_results = None
    for attempt in range(8):
        delay = [4, 5, 6, 7, 8, 9, 10, 12][attempt]
        print(f"   Tentativa {attempt+1}/8 - aguardando {delay}s...", end=" ", flush=True)
        time.sleep(delay)
        
        resp = session.get(redirect_url, timeout=15)
        html = resp.text
        
        has_cars = 'class="carCardWeb"' in html or 'class="price pr-euros"' in html
        print(f"HTML: {len(html)} bytes, carros: {has_cars}")
        
        if has_cars:
            html_results = html
            break
    
    if not html_results:
        print("❌ Timeout - sem resultados")
        return
    
    # ANÁLISE DO HTML
    print(f"\n{'='*70}")
    print(f"🔍 ANÁLISE DO HTML DA HOMEPAGE (após polling)")
    print(f"{'='*70}")
    
    # Contar artigos
    articles = re.findall(r'<article[^>]*>', html_results)
    print(f"   <article> tags: {len(articles)}")
    
    # Verificar carros específicos
    cars_to_check = ['Jogger', 'Lodgy', 'Sharan', 'Peugeot 5008', 'Dacia', 'Citroen C4 Picasso']
    for car in cars_to_check:
        count = html_results.lower().count(car.lower())
        print(f"   '{car}': {count} ocorrências")
    
    # Parse completo
    print(f"\n📌 Parse completo do HTML...")
    cars = parse_carjet_html_complete(html_results)
    print(f"   Total: {len(cars)} carros")
    
    # Procurar Jogger
    joggers = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
    print(f"\n   Dacia Jogger: {len(joggers)}")
    for j in joggers:
        print(f"      → {j.get('supplier', '?'):25s} | {j.get('price', '?'):>12s}")
    
    # Contar por grupo
    from collections import defaultdict
    by_group = defaultdict(int)
    for car in cars:
        g = car.get('grupo', car.get('group', '?'))
        by_group[g] += 1
    
    print(f"\n   Por grupo:")
    for g, cnt in sorted(by_group.items()):
        print(f"      {g:10s}: {cnt}")
    
    # Contar por supplier
    by_sup = defaultdict(int)
    for car in cars:
        s = car.get('supplier', '?')
        by_sup[s] += 1
    
    print(f"\n   Top suppliers:")
    for s, cnt in sorted(by_sup.items(), key=lambda x: -x[1])[:15]:
        print(f"      {s:25s}: {cnt}")
    
    # Verificar se há artigos escondidos (hidden)
    hidden = re.findall(r'<article[^>]*class="[^"]*hidden[^"]*"', html_results)
    print(f"\n   Artigos hidden: {len(hidden)}")
    
    # Verificar data-agrp nos artigos
    agrp_attrs = re.findall(r'data-agrp="([^"]*)"', html_results)
    if agrp_attrs:
        agrp_counts = defaultdict(int)
        for a in agrp_attrs:
            agrp_counts[a] += 1
        print(f"\n   data-agrp encontrados:")
        for a, cnt in sorted(agrp_counts.items()):
            print(f"      {a}: {cnt}")
    else:
        print(f"\n   data-agrp: NÃO encontrado")
    
    # Salvar HTML para análise
    with open('carjet_homepage_full.html', 'w', encoding='utf-8') as f:
        f.write(html_results)
    print(f"\n   HTML salvo em: carjet_homepage_full.html ({len(html_results)} bytes)")


if __name__ == '__main__':
    main()
