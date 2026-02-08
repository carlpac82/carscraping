#!/usr/bin/env python3
"""
Teste mobile: abrir CarJet, LIMPAR filtro Automático, depois ver categorias
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
from collections import defaultdict

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

def count_visible(driver):
    articles = driver.find_elements(By.CSS_SELECTOR, 'article')
    return [a for a in articles if a.is_displayed()]

def extract_cars(driver):
    cars = []
    for art in count_visible(driver):
        try:
            name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, [class*="title"]')
            name = name_el[0].text.strip() if name_el else '?'
            if 'ou similar' in name.lower():
                name = name[:name.lower().index('ou similar')].strip()
            supplier = art.get_attribute('data-prv') or '?'
            price = '?'
            for p in art.find_elements(By.CSS_SELECTOR, '[class*="price"]'):
                txt = p.text.strip()
                if '€' in txt and len(txt) < 25:
                    price = txt
                    break
            if name and name != '?':
                cars.append((name.lower().strip(), supplier.strip(), price.strip()))
        except:
            continue
    return cars

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
        
        print("📱 Abrindo CarJet mobile...")
        driver.get(url)
        time.sleep(12)
        
        # ── ANTES DE LIMPAR ──
        cars_before = extract_cars(driver)
        print(f"\n{'='*60}")
        print(f"📱 ANTES (com filtro Automático): {len(cars_before)} carros")
        print(f"{'='*60}")
        driver.save_screenshot(f"{ss_dir}/limpar_01_antes.png")
        
        jogger_before = [c for c in cars_before if 'jogger' in c[0]]
        print(f"   Dacia Jogger: {len(jogger_before)}")
        
        # ── LIMPAR FILTRO ──
        print(f"\n🧹 Limpando filtro Automático...")
        
        # Método 1: Clicar em "Limpar tudo"
        try:
            limpar_els = driver.find_elements(By.XPATH, "//a[contains(text(), 'Limpar tudo')] | //span[contains(text(), 'Limpar tudo')]")
            if limpar_els:
                print(f"   Encontrado 'Limpar tudo' - clicando...")
                limpar_els[0].click()
                time.sleep(5)
            else:
                print("   'Limpar tudo' não encontrado")
        except Exception as e:
            print(f"   Erro: {e}")
        
        # Método 2: Clicar no X do filtro Automático
        try:
            auto_x = driver.find_elements(By.CSS_SELECTOR, 'span.filter-btn.active')
            if auto_x:
                for btn in auto_x:
                    if 'Automático' in btn.text or 'automático' in btn.text.lower():
                        print(f"   Clicando no botão Automático para desactivar...")
                        btn.click()
                        time.sleep(5)
                        break
        except Exception as e:
            print(f"   Erro método 2: {e}")
        
        # Método 3: Via JavaScript - trigger click no chkTransA
        try:
            driver.execute_script("""
                var chk = document.getElementById('chkTransA');
                if (chk) { 
                    $(chk).trigger('click');
                }
            """)
            time.sleep(3)
        except:
            pass
        
        driver.save_screenshot(f"{ss_dir}/limpar_02_depois.png")
        
        # ── DEPOIS DE LIMPAR ──
        cars_after = extract_cars(driver)
        print(f"\n{'='*60}")
        print(f"📱 DEPOIS (sem filtro): {len(cars_after)} carros")
        print(f"{'='*60}")
        
        jogger_after = [c for c in cars_after if 'jogger' in c[0]]
        print(f"   Dacia Jogger: {len(jogger_after)}")
        for j in jogger_after:
            print(f"      {j[0]:35s} | {j[1]:8s} | {j[2]}")
        
        # Verificar filtros activos
        filter_active = driver.find_elements(By.CSS_SELECTOR, 'span.filter-btn.active')
        print(f"\n   Filtros activos: {len(filter_active)}")
        for f in filter_active:
            print(f"      {f.text[:50]}")
        
        # ── CATEGORIAS SEM FILTRO ──
        print(f"\n{'='*60}")
        print(f"📂 CATEGORIAS (sem filtro Automático)")
        print(f"{'='*60}")
        
        all_cat_cars = []
        for cat_code, cat_name in CATEGORIES.items():
            print(f"\n   🔍 {cat_name} ({cat_code})...", end=" ", flush=True)
            try:
                driver.execute_script(f"filterAgrupVeh('{cat_code}')")
                time.sleep(4)
                
                cars = extract_cars(driver)
                all_cat_cars.extend(cars)
                
                joggers = [c for c in cars if 'jogger' in c[0]]
                print(f"{len(cars)} carros | Jogger: {len(joggers)}")
                
                if cat_code == 'VANS':
                    driver.save_screenshot(f"{ss_dir}/limpar_03_vans.png")
                    print(f"   Carros VANS:")
                    for c in cars:
                        print(f"      {c[0]:35s} | {c[1]:8s} | {c[2]}")
            except Exception as e:
                print(f"❌ {e}")
        
        # ── RESUMO ──
        homepage_set = set(cars_after)
        cat_set = set(all_cat_cars)
        combined = homepage_set | cat_set
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMO (SEM filtro Automático)")
        print(f"{'='*60}")
        print(f"   Homepage: {len(homepage_set)} únicos")
        print(f"   Categorias: {len(cat_set)} únicos")
        print(f"   Combinado: {len(combined)}")
        
        joggers_total = [c for c in combined if 'jogger' in c[0]]
        print(f"\n   Dacia Jogger total: {len(joggers_total)}")
        for j in sorted(joggers_total, key=lambda x: x[2]):
            print(f"      {j[0]:35s} | {j[1]:8s} | {j[2]}")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
