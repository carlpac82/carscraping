#!/usr/bin/env python3
"""
Teste simples: abrir CarJet mobile SEM clicar em nada
Verificar se o filtro Automático aparece por defeito ou não
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os

UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

ss_dir = 'screenshots_mobile'
os.makedirs(ss_dir, exist_ok=True)

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
        url = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"
        
        print("📱 Abrindo CarJet mobile - SEM TOCAR EM NADA...")
        driver.get(url)
        time.sleep(15)
        
        driver.save_screenshot(f"{ss_dir}/clean_01_homepage.png")
        print(f"   Screenshot: {ss_dir}/clean_01_homepage.png")
        
        # Verificar filtros activos
        html = driver.page_source
        has_auto_filter = 'Automático' in html and ('Filtros ativ' in html or 'filtros-activ' in html.lower())
        print(f"\n   'Automático' + 'Filtros ativos' no HTML: {has_auto_filter}")
        print(f"   'Automático' no HTML: {'Automático' in html}")
        
        # Contar artigos
        articles = driver.find_elements(By.CSS_SELECTOR, 'article')
        visible = [a for a in articles if a.is_displayed()]
        print(f"   Artigos: {len(articles)} total, {len(visible)} visíveis")
        
        # Procurar Jogger
        jogger_in_html = html.lower().count('jogger')
        print(f"   'Jogger' no HTML: {jogger_in_html}")
        
        # Verificar se há filtro activo visível
        filter_els = driver.find_elements(By.XPATH, "//*[contains(text(), 'Filtros ativ')]")
        if filter_els:
            print(f"\n   ⚠️ FILTROS ACTIVOS encontrados:")
            for f in filter_els:
                print(f"      {f.text[:100]}")
        else:
            print(f"\n   ✅ Sem filtros activos visíveis")
        
        # Listar primeiros carros
        print(f"\n   Primeiros 5 carros:")
        for art in visible[:5]:
            try:
                name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, [class*="title"]')
                name = name_el[0].text.strip() if name_el else '?'
                if 'ou similar' in name.lower():
                    name = name[:name.lower().index('ou similar')].strip()
                supplier = art.get_attribute('data-prv') or '?'
                print(f"      {name:35s} | {supplier}")
            except:
                continue
        
        input("\n👀 VÊ O CHROME - Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
