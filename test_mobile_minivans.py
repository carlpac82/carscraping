#!/usr/bin/env python3
"""
Teste visual MOBILE (iPhone) - mesmo user-agent que o scraper real
Verificar Minivans e se captura os 2 Dacia Jogger da Surprice
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Mesmo user-agent que o scraper usa em carjet_requests.py
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    # MOBILE user-agent (igual ao scraper)
    opts.add_argument(f'user-agent={UA_IPHONE}')
    # Simular dimensões iPhone
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": UA_IPHONE
    }
    opts.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("📱 Abrindo CarJet em modo MOBILE (iPhone)...")
        driver.get(SESSION_URL)
        print("⏳ Aguardando carregamento...")
        time.sleep(12)
        
        # 1. Homepage mobile
        html = driver.page_source
        
        # Verificar se é versão mobile
        is_mobile = 'carCardMob' in html
        is_desktop = 'carCardWeb' in html
        print(f"\n   carCardMob: {is_mobile} | carCardWeb: {is_desktop}")
        
        # Contar artigos
        articles = driver.find_elements(By.CSS_SELECTOR, 'article')
        visible = [a for a in articles if a.is_displayed()]
        print(f"   Artigos: {len(articles)} total, {len(visible)} visíveis")
        
        # Verificar Jogger no HTML
        jogger_html = html.lower().count('jogger')
        print(f"   'Jogger' no HTML: {jogger_html}")
        
        # 2. Listar carros visíveis na homepage
        print(f"\n{'='*60}")
        print(f"📱 HOMEPAGE MOBILE: {len(visible)} carros")
        print(f"{'='*60}")
        
        for art in visible[:10]:
            try:
                name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title, [class*="title"]')
                name = name_el[0].text.strip() if name_el else '?'
                supplier = art.get_attribute('data-prv') or '?'
                print(f"   {name:40s} | {supplier}")
            except:
                continue
        if len(visible) > 10:
            print(f"   ... e mais {len(visible) - 10}")
        
        # 3. Tentar clicar em Minivans
        print(f"\n{'='*60}")
        print(f"🚐 TENTANDO MINIVANS...")
        print(f"{'='*60}")
        
        try:
            driver.execute_script("filterAgrupVeh('VANS')")
            time.sleep(5)
            
            articles_vans = driver.find_elements(By.CSS_SELECTOR, 'article')
            visible_vans = [a for a in articles_vans if a.is_displayed()]
            print(f"   Minivans: {len(visible_vans)} carros")
            
            # Listar todos
            for art in visible_vans:
                try:
                    name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title, [class*="title"]')
                    name = name_el[0].text.strip() if name_el else '?'
                    supplier = art.get_attribute('data-prv') or '?'
                    
                    price_els = art.find_elements(By.CSS_SELECTOR, '[class*="price"]')
                    price = '?'
                    for p in price_els:
                        txt = p.text.strip()
                        if '€' in txt and len(txt) < 20:
                            price = txt
                            break
                    
                    print(f"   {name:40s} | {supplier:8s} | {price}")
                except:
                    continue
            
            # Procurar Jogger
            jogger_count = sum(1 for a in visible_vans 
                for ne in [a.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title, [class*="title"]')]
                if ne and 'jogger' in ne[0].text.lower())
            print(f"\n   Dacia Jogger encontrados: {jogger_count}")
            
        except Exception as e:
            print(f"   filterAgrupVeh não disponível: {e}")
            print("   Versão mobile pode não ter esta função")
        
        # 4. Verificar todas as categorias no mobile
        print(f"\n{'='*60}")
        print(f"📂 TODAS AS CATEGORIAS (mobile)")
        print(f"{'='*60}")
        
        categories = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']
        for cat in categories:
            try:
                driver.execute_script(f"filterAgrupVeh('{cat}')")
                time.sleep(3)
                arts = driver.find_elements(By.CSS_SELECTOR, 'article')
                vis = [a for a in arts if a.is_displayed()]
                print(f"   {cat:6s}: {len(vis)} carros")
            except:
                print(f"   {cat:6s}: erro")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
