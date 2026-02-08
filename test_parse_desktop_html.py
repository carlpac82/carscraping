#!/usr/bin/env python3
"""
Teste: abrir CarJet DESKTOP (sem mobile emulation), capturar HTML da homepage
e testar o parse_carjet_html_complete para ver quantos carros captura
Comparar com o que o Railway captura
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

# Usar MESMO user-agent iPhone que o Railway (mas SEM mobile emulation)
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

SESSION_URL = "https://www.carjet.com/do/list/pt?s=56bed9eb-1d31-4a64-933c-e3d13428f2e8&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    # User-agent iPhone MAS sem mobile emulation (janela desktop)
    opts.add_argument(f'user-agent={UA_IPHONE}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("📌 Abrindo CarJet (desktop window, iPhone UA)...")
        driver.get(SESSION_URL)
        time.sleep(15)
        
        html = driver.page_source
        is_desktop = 'carCardWeb' in html
        is_mobile = 'carCardMob' in html
        print(f"   Desktop: {is_desktop} | Mobile: {is_mobile}")
        
        # Salvar HTML
        with open('carjet_desktop_test.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   HTML salvo: {len(html)} bytes")
        
        # Contar artigos e Jogger no HTML bruto
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('article')
        print(f"   Artigos: {len(articles)}")
        
        jogger_html = html.lower().count('jogger')
        print(f"   'jogger' no HTML: {jogger_html}")
        
        # Listar TODOS os Jogger com data-prv e preço
        print(f"\n{'='*80}")
        print(f"TODOS OS DACIA JOGGER NO HTML:")
        print(f"{'='*80}")
        for i, art in enumerate(articles):
            h2 = art.find('h2')
            if h2 and 'jogger' in h2.get_text().lower():
                prv = art.get('data-prv', '?')
                order = art.get('data-order', '?')
                price_span = art.find('span', class_=lambda x: x and 'pr-euros' in x and 'price' in x if x else False)
                price = price_span.get_text(strip=True) if price_span else '?'
                # Logo do supplier
                logo = art.find('img', src=re.compile(r'logo_'))
                logo_name = logo.get('alt', '?') if logo else '?'
                classes = ' '.join(art.get('class', []))
                print(f"   #{order:3s} | prv={prv:6s} | {logo_name:25s} | {price:15s} | classes={classes}")
        
        # Agora testar o parse
        print(f"\n{'='*80}")
        print(f"RESULTADO DO parse_carjet_html_complete:")
        print(f"{'='*80}")
        from carjet_direct import parse_carjet_html_complete
        cars = parse_carjet_html_complete(html)
        print(f"   Total carros parsed: {len(cars)}")
        
        jogger_parsed = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name') or '').lower()]
        print(f"   Jogger parsed: {len(jogger_parsed)}")
        for j in jogger_parsed:
            print(f"      {j.get('car_name','?'):30s} | {j.get('supplier','?'):25s} | {j.get('price','?')}")
        
        # Comparar: quais Jogger estão no HTML mas NÃO no parse?
        print(f"\n{'='*80}")
        print(f"COMPARAÇÃO:")
        print(f"{'='*80}")
        
        # Contar Jogger por supplier no HTML
        jogger_html_suppliers = {}
        for art in articles:
            h2 = art.find('h2')
            if h2 and 'jogger' in h2.get_text().lower():
                prv = art.get('data-prv', '?')
                price_span = art.find('span', class_=lambda x: x and 'pr-euros' in x and 'price' in x if x else False)
                price = price_span.get_text(strip=True) if price_span else '?'
                key = f"{prv}|{price}"
                jogger_html_suppliers[key] = jogger_html_suppliers.get(key, 0) + 1
        
        # Contar Jogger por supplier no parse
        jogger_parse_suppliers = {}
        for j in jogger_parsed:
            sup = j.get('supplier', '?')
            price = j.get('price', '?')
            key = f"{sup}|{price}"
            jogger_parse_suppliers[key] = jogger_parse_suppliers.get(key, 0) + 1
        
        print(f"   HTML Jogger: {len(jogger_html_suppliers)} únicos")
        for k, v in sorted(jogger_html_suppliers.items()):
            print(f"      {k} (x{v})")
        
        print(f"   Parse Jogger: {len(jogger_parse_suppliers)} únicos")
        for k, v in sorted(jogger_parse_suppliers.items()):
            print(f"      {k} (x{v})")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
