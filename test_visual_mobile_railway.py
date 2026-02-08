#!/usr/bin/env python3
"""
Teste visual Chrome MOBILE (iPhone) - simula exactamente o que o Railway faz
Abre Chrome em modo iPhone, navega pelo CarJet, conta carros e suppliers
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
from collections import defaultdict

# Mesmo user-agent que carjet_requests.py usa no Railway
UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

CATEGORIES = {
    'MINI': 'Pequeno',
    'COMP': 'Médio',
    'FAMI': 'Grande',
    'ESTA': 'Station Wagon',
    'SUVS': 'SUVs',
    'VANS': 'Minivans',
    'LUXU': 'Premium',
    'AUTO': 'Automático',
}

ss_dir = 'screenshots_mobile'
os.makedirs(ss_dir, exist_ok=True)


def extract_cars(driver):
    """Extrai carros visíveis - tenta múltiplos selectores (mobile + desktop)"""
    cars = []
    # Tentar vários selectores
    articles = driver.find_elements(By.CSS_SELECTOR, 'article')
    if not articles:
        articles = driver.find_elements(By.CSS_SELECTOR, '[class*="carCard"]')
    
    for art in articles:
        try:
            if not art.is_displayed():
                continue
            
            # Nome
            name = ''
            for sel in ['h2', 'h3', '.cl--title', '[class*="title"]', '[class*="car-name"]']:
                els = art.find_elements(By.CSS_SELECTOR, sel)
                if els and els[0].text.strip():
                    name = els[0].text.strip()
                    # Limpar "ou similar" etc
                    if 'ou similar' in name.lower():
                        name = name[:name.lower().index('ou similar')].strip()
                    break
            
            if not name:
                continue
            
            # Supplier
            supplier = art.get_attribute('data-prv') or ''
            
            # Se data-prv vazio, tentar extrair do logo
            if not supplier:
                logos = art.find_elements(By.CSS_SELECTOR, 'img[src*="logo"]')
                for logo in logos:
                    src = logo.get_attribute('src') or ''
                    import re
                    m = re.search(r'logo[_-]([A-Z0-9]+)', src, re.IGNORECASE)
                    if m:
                        supplier = m.group(1)
                        break
            
            if not supplier:
                supplier = '?'
            
            # Preço
            price = '?'
            price_els = art.find_elements(By.CSS_SELECTOR, '[class*="price"]')
            for p in price_els:
                txt = p.text.strip()
                if '€' in txt and len(txt) < 25:
                    price = txt
                    break
            
            cars.append((name.lower().strip(), supplier.strip(), price.strip()))
        except:
            continue
    return cars


def main():
    opts = Options()
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    # Emulação iPhone (igual ao scraper Railway)
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": UA_IPHONE
    }
    opts.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Usar sessão existente
        url = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"
        
        print("=" * 60)
        print("📱 TESTE VISUAL MOBILE (iPhone) - COMO O RAILWAY")
        print("=" * 60)
        
        print(f"\n📌 Abrindo CarJet mobile...")
        driver.get(url)
        print("⏳ Aguardando carregamento...")
        time.sleep(12)
        driver.save_screenshot(f"{ss_dir}/01_homepage_mobile.png")
        
        # ── HOMEPAGE ──
        homepage_cars = extract_cars(driver)
        print(f"\n{'='*60}")
        print(f"📱 HOMEPAGE MOBILE: {len(homepage_cars)} carros")
        print(f"{'='*60}")
        
        # Por supplier
        sup_counts = defaultdict(int)
        for _, sup, _ in homepage_cars:
            sup_counts[sup] += 1
        
        print(f"\n   Por supplier:")
        for sup, cnt in sorted(sup_counts.items(), key=lambda x: -x[1]):
            print(f"      {sup:12s}: {cnt}")
        
        # Jogger
        joggers = [(n, s, p) for n, s, p in homepage_cars if 'jogger' in n]
        print(f"\n   Dacia Jogger: {len(joggers)}")
        for n, s, p in joggers:
            print(f"      {n:35s} | {s:8s} | {p}")
        
        # Primeiros 10 carros
        print(f"\n   Primeiros 10 carros:")
        for n, s, p in homepage_cars[:10]:
            print(f"      {n:35s} | {s:8s} | {p}")
        
        # ── CATEGORIAS ──
        print(f"\n{'='*60}")
        print(f"📂 CATEGORIAS MOBILE")
        print(f"{'='*60}")
        
        all_cat_cars = []
        for cat_code, cat_name in CATEGORIES.items():
            print(f"\n   🔍 {cat_name} ({cat_code})...", end=" ", flush=True)
            try:
                driver.execute_script(f"filterAgrupVeh('{cat_code}')")
                time.sleep(4)
                driver.save_screenshot(f"{ss_dir}/cat_{cat_code}_mobile.png")
                
                cars = extract_cars(driver)
                all_cat_cars.extend(cars)
                
                joggers_cat = [(n, s, p) for n, s, p in cars if 'jogger' in n]
                print(f"{len(cars)} carros | Jogger: {len(joggers_cat)}")
            except Exception as e:
                print(f"❌ {e}")
        
        # ── DEDUPLICAÇÃO ──
        all_cat_set = set(all_cat_cars)
        homepage_set = set(homepage_cars)
        combined = homepage_set | all_cat_set
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMO MOBILE")
        print(f"{'='*60}")
        print(f"   Homepage: {len(homepage_set)} carros únicos")
        print(f"   Categorias (bruto): {len(all_cat_cars)}")
        print(f"   Categorias (únicos): {len(all_cat_set)}")
        print(f"   Combinado: {len(combined)}")
        print(f"   Extra nas categorias: {len(all_cat_set - homepage_set)}")
        print(f"   Só na homepage: {len(homepage_set - all_cat_set)}")
        
        # Jogger final
        joggers_all = [(n, s, p) for n, s, p in combined if 'jogger' in n]
        print(f"\n   Dacia Jogger (total único): {len(joggers_all)}")
        for n, s, p in sorted(joggers_all, key=lambda x: x[2]):
            print(f"      {n:35s} | {s:8s} | {p}")
        
        # Suppliers combinados
        sup_combined = defaultdict(int)
        for _, sup, _ in combined:
            sup_combined[sup] += 1
        print(f"\n   Suppliers ({len(sup_combined)}):")
        for sup, cnt in sorted(sup_combined.items(), key=lambda x: -x[1]):
            print(f"      {sup:12s}: {cnt}")
        
        print(f"\n   Screenshots em: {ss_dir}/")
        
        print(f"\n{'='*60}")
        input("👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()
        print("🔒 Fechado")


if __name__ == '__main__':
    main()
