#!/usr/bin/env python3
"""
Capturar HTML do Selenium (MOBILE iPhone) para a categoria VANS
e analisar os artigos do Dacia Jogger - especialmente o de Oferta Limitada
Exactamente como o Railway faz
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": UA_IPHONE
    }
    opts.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("📱 Abrindo CarJet (iPhone mobile)...")
        driver.get(SESSION_URL)
        time.sleep(12)
        
        # LIMPAR filtro Automático primeiro
        print("🧹 Limpando filtro Automático...")
        try:
            limpar = driver.find_elements(By.XPATH, "//a[contains(text(), 'Limpar tudo')] | //span[contains(text(), 'Limpar tudo')]")
            if limpar:
                limpar[0].click()
                time.sleep(5)
                print("   ✅ Clicou 'Limpar tudo'")
            else:
                # Tentar clicar no X do filtro Automático
                auto_btns = driver.find_elements(By.CSS_SELECTOR, 'span.filter-btn.active')
                for btn in auto_btns:
                    if 'Automático' in btn.text or 'automático' in btn.text.lower():
                        btn.click()
                        time.sleep(5)
                        print("   ✅ Desactivou filtro Automático")
                        break
        except Exception as e:
            print(f"   ⚠️ Erro ao limpar: {e}")
        
        time.sleep(3)
        
        # Clicar em Minivans
        print("🚐 Clicando em Minivans...")
        driver.execute_script("filterAgrupVeh('VANS')")
        time.sleep(5)
        
        # Capturar HTML completo
        html = driver.page_source
        
        # Salvar HTML completo
        with open('carjet_vans_selenium.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   HTML salvo: carjet_vans_selenium.html ({len(html)} bytes)")
        
        # Analisar artigos com Jogger
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('article')
        print(f"\n   Total artigos: {len(articles)}")
        
        jogger_articles = []
        for i, art in enumerate(articles):
            text = art.get_text().lower()
            if 'jogger' in text:
                jogger_articles.append((i, art))
        
        print(f"   Artigos com 'Jogger': {len(jogger_articles)}")
        
        for idx, (i, art) in enumerate(jogger_articles):
            print(f"\n{'='*80}")
            print(f"   JOGGER #{idx+1} (artigo #{i})")
            print(f"{'='*80}")
            
            # Atributos do article
            print(f"   Atributos: {dict(art.attrs)}")
            
            # data-prv
            prv = art.get('data-prv', '?')
            print(f"   data-prv: {prv}")
            
            # Classe
            classes = art.get('class', [])
            print(f"   Classes: {classes}")
            
            # Preço
            price_spans = art.find_all('span', class_=lambda x: x and 'price' in ' '.join(x) if x else False)
            for ps in price_spans:
                cls = ps.get('class', [])
                txt = ps.get_text(strip=True)
                print(f"   Preço span: classes={cls} text='{txt}'")
            
            # Oferta especial / não reembolsável
            special = art.find_all(string=re.compile(r'(oferta|especial|limitada|reembols|non.?refund)', re.IGNORECASE))
            if special:
                print(f"   ⚠️ OFERTA ESPECIAL: {[s.strip()[:80] for s in special]}")
            
            # Nome
            for tag in art.find_all(['h2', 'h3', 'h4']):
                print(f"   Título ({tag.name}): {tag.get_text(strip=True)[:80]}")
            
            # HTML resumido (primeiros 500 chars)
            art_html = str(art)
            print(f"   HTML ({len(art_html)} chars):")
            print(f"   {art_html[:800]}")
            print(f"   ...")
        
        # Agora testar o parse_carjet_html_complete com este HTML
        print(f"\n{'='*80}")
        print(f"🔍 TESTANDO parse_carjet_html_complete com HTML do Selenium")
        print(f"{'='*80}")
        
        from carjet_direct import parse_carjet_html_complete
        cars = parse_carjet_html_complete(html)
        
        jogger_parsed = [c for c in cars if 'jogger' in (c.get('car') or c.get('car_name', '')).lower()]
        print(f"\n   Jogger no parse: {len(jogger_parsed)}")
        for j in jogger_parsed:
            print(f"      {j.get('car_name','?'):30s} | {j.get('supplier','?'):20s} | {j.get('price','?')}")
        
        # Comparar: artigos no HTML vs parse
        surprice_jogger_html = sum(1 for _, art in jogger_articles if art.get('data-prv', '') == 'SUR')
        surprice_jogger_parse = sum(1 for j in jogger_parsed if 'sur' in j.get('supplier', '').lower())
        print(f"\n   Jogger Surprice no HTML: {surprice_jogger_html}")
        print(f"   Jogger Surprice no parse: {surprice_jogger_parse}")
        
        if surprice_jogger_html > surprice_jogger_parse:
            print(f"   ⚠️ PARSE PERDE {surprice_jogger_html - surprice_jogger_parse} Jogger Surprice!")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
