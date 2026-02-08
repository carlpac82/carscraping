#!/usr/bin/env python3
"""
Debug: Comparar HTML do browser (Selenium) vs requests para Minivans
Objectivo: entender porque Dacia Jogger aparece no browser mas não no scraper
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
from collections import defaultdict

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("📌 Abrindo CarJet...")
        driver.get(SESSION_URL)
        time.sleep(10)
        
        # 1. Homepage - contar carros
        articles_home = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible_home = [a for a in articles_home if a.is_displayed()]
        print(f"\n{'='*70}")
        print(f"📋 HOMEPAGE: {len(visible_home)} carros visíveis ({len(articles_home)} total no DOM)")
        print(f"{'='*70}")
        
        # Verificar se há artigos escondidos
        hidden_home = len(articles_home) - len(visible_home)
        print(f"   Visíveis: {len(visible_home)} | Escondidos: {hidden_home}")
        
        # Contar TODOS os artigos no DOM (incluindo escondidos)
        html_home = driver.page_source
        all_articles_html = re.findall(r'<article[^>]*>', html_home)
        print(f"   <article> tags no HTML: {len(all_articles_html)}")
        
        # Verificar data-agrp nos artigos
        agrp_values = re.findall(r'data-agrp="([^"]*)"', html_home)
        if agrp_values:
            agrp_counts = defaultdict(int)
            for a in agrp_values:
                agrp_counts[a] += 1
            print(f"\n   data-agrp no DOM:")
            for a, cnt in sorted(agrp_counts.items()):
                print(f"      {a}: {cnt} artigos")
        
        # Verificar Jogger no HTML
        jogger_count = html_home.lower().count('jogger')
        dacia_count = html_home.lower().count('dacia')
        print(f"\n   'Jogger' no HTML: {jogger_count} ocorrências")
        print(f"   'Dacia' no HTML: {dacia_count} ocorrências")
        
        # 2. Clicar em Minivans
        print(f"\n{'='*70}")
        print(f"🔍 CLICANDO EM MINIVANS...")
        print(f"{'='*70}")
        
        driver.execute_script("filterAgrupVeh('VANS')")
        time.sleep(5)
        
        articles_vans = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible_vans = [a for a in articles_vans if a.is_displayed()]
        print(f"   Após filtro VANS: {len(visible_vans)} carros visíveis ({len(articles_vans)} total no DOM)")
        
        # Extrair carros visíveis nas Minivans
        print(f"\n   Carros visíveis nas Minivans:")
        for art in visible_vans:
            try:
                name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title')
                name = name_el[0].text.strip() if name_el else '?'
                supplier = art.get_attribute('data-prv') or '?'
                
                # Preço
                price_els = art.find_elements(By.CSS_SELECTOR, '.price.pr-euros')
                price = '?'
                for p in price_els:
                    txt = p.text.strip()
                    if txt and '€' in txt:
                        price = txt
                        break
                
                # data-agrp
                agrp = art.get_attribute('data-agrp') or '?'
                
                print(f"      {name:40s} | {supplier:8s} | {price:>12s} | agrp={agrp}")
            except:
                continue
        
        # 3. Verificar o JavaScript filterAgrupVeh
        print(f"\n{'='*70}")
        print(f"🔧 COMO FUNCIONA filterAgrupVeh?")
        print(f"{'='*70}")
        
        # Tentar obter o código da função
        try:
            func_code = driver.execute_script("return filterAgrupVeh.toString()")
            print(f"   Código da função:")
            print(f"   {func_code[:1000]}")
        except Exception as e:
            print(f"   Não conseguiu obter código: {e}")
        
        # 4. Verificar se o filtro é client-side ou server-side
        print(f"\n{'='*70}")
        print(f"🔍 FILTRO CLIENT-SIDE vs SERVER-SIDE?")
        print(f"{'='*70}")
        
        # Voltar a "Todos"
        try:
            driver.execute_script("filterAgrupVeh('')")
            time.sleep(3)
            articles_all = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
            visible_all = [a for a in articles_all if a.is_displayed()]
            print(f"   Após voltar a 'Todos': {len(visible_all)} visíveis ({len(articles_all)} no DOM)")
            
            # Se o número de artigos no DOM não mudou, é client-side
            if len(articles_all) == len(articles_home):
                print(f"   ✅ FILTRO É CLIENT-SIDE (DOM não mudou: {len(articles_all)} artigos)")
            else:
                print(f"   ⚠️ FILTRO É SERVER-SIDE (DOM mudou: {len(articles_home)} → {len(articles_all)})")
        except:
            pass
        
        # 5. Verificar artigos com data-agrp=VANS que estão escondidos na homepage
        print(f"\n{'='*70}")
        print(f"🔍 ARTIGOS VANS ESCONDIDOS NA HOMEPAGE?")
        print(f"{'='*70}")
        
        # Voltar a todos primeiro
        driver.execute_script("filterAgrupVeh('')")
        time.sleep(3)
        
        all_arts = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        vans_in_dom = []
        for art in all_arts:
            agrp = art.get_attribute('data-agrp') or ''
            if 'VANS' in agrp.upper() or 'VAN' in agrp.upper():
                name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title')
                name = name_el[0].text.strip() if name_el else '?'
                visible = art.is_displayed()
                vans_in_dom.append((name, agrp, visible))
        
        print(f"   Artigos com data-agrp contendo 'VAN': {len(vans_in_dom)}")
        for name, agrp, vis in vans_in_dom:
            status = "✅ visível" if vis else "❌ escondido"
            print(f"      {name:40s} | agrp={agrp} | {status}")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
