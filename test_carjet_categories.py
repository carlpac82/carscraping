#!/usr/bin/env python3
"""
Teste visual CarJet - Navegar pelas categorias para ver todos os carros
Abre Chrome visível e clica em cada categoria (Minivans, SUVs, etc.)
NOTA: CARG (carrinhas comerciais) excluído - não fazemos scraping dessas
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os
from datetime import datetime

# Categorias a testar (sem CARG - carrinhas comerciais, não necessário)
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

def setup_chrome_visual():
    """Chrome visível (não headless) para teste"""
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return opts


def wait_for_cars(driver, max_wait=8):
    """Aguarda até carros aparecerem na página (polling rápido)"""
    for i in range(max_wait):
        time.sleep(1)
        # Verificar se loading terminou
        loading = driver.find_elements(By.CSS_SELECTOR, '.loading, .spinner, [class*="loading"]')
        has_loading = any(l.is_displayed() for l in loading) if loading else False
        
        articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible = [a for a in articles if a.is_displayed()]
        
        if len(visible) > 0 and not has_loading:
            return len(visible)
    return 0


def count_cars(driver):
    """Conta carros visíveis na página"""
    articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
    visible = [a for a in articles if a.is_displayed() and 'hidden' not in (a.get_attribute('class') or '')]
    return len(visible)


def extract_cars_from_page(driver):
    """Extrai info dos carros visíveis"""
    cars = []
    articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
    
    for art in articles:
        try:
            if not art.is_displayed():
                continue
            if 'hidden' in (art.get_attribute('class') or ''):
                continue
            
            # Nome do carro
            name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title')
            name = name_el[0].text.strip() if name_el else '?'
            
            # Supplier
            supplier = art.get_attribute('data-prv') or '?'
            
            # Preço
            price_el = art.find_elements(By.CSS_SELECTOR, '.price.pr-euros')
            price = '?'
            for p in price_el:
                txt = p.text.strip()
                if txt and '€' in txt and 'day' not in (p.get_attribute('class') or '').lower():
                    price = txt
                    break
            
            # Foto
            img_el = art.find_elements(By.CSS_SELECTOR, '.thbCarDest img, .cl--car img')
            photo = img_el[0].get_attribute('src') if img_el else ''
            
            cars.append({
                'name': name,
                'supplier': supplier,
                'price': price,
                'photo': photo
            })
        except:
            continue
    
    return cars


def test_categories():
    """Teste principal - abre CarJet e navega pelas categorias"""
    
    # Screenshots dir
    ss_dir = 'screenshots_categories'
    os.makedirs(ss_dir, exist_ok=True)
    
    print("=" * 70)
    print("🚗 TESTE VISUAL CARJET - CATEGORIAS")
    print("=" * 70)
    
    # Setup Chrome
    opts = setup_chrome_visual()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    all_cars = {}
    
    try:
        # Usar a URL da sessão existente
        url = "https://www.carjet.com/do/list/pt?s=acc2519f-b521-4f31-b31e-3577274fd60a&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"
        
        print(f"\n📌 Abrindo página de resultados...")
        print(f"   URL: {url[:80]}...")
        driver.get(url)
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        time.sleep(10)
        
        # Screenshot inicial
        driver.save_screenshot(f"{ss_dir}/00_pagina_inicial.png")
        
        # Contar carros na página inicial
        n_initial = count_cars(driver)
        initial_cars = extract_cars_from_page(driver)
        print(f"\n✅ Página inicial carregada: {n_initial} carros visíveis")
        
        all_cars['TODOS'] = initial_cars
        
        for car in initial_cars[:5]:
            print(f"   - {car['name']} | {car['supplier']} | {car['price']}")
        if len(initial_cars) > 5:
            print(f"   ... e mais {len(initial_cars) - 5} carros")
        
        # Agora navegar por cada categoria
        print("\n" + "=" * 70)
        print("📂 NAVEGANDO PELAS CATEGORIAS")
        print("=" * 70)
        
        for cat_code, cat_name in CATEGORIES.items():
            print(f"\n{'─' * 50}")
            print(f"🔍 Categoria: {cat_name} ({cat_code})")
            print(f"{'─' * 50}")
            
            try:
                # Clicar no filtro de categoria via JavaScript
                driver.execute_script(f"filterAgrupVeh('{cat_code}')")
                
                print(f"   ⏳ Aguardando carregamento...")
                n_loaded = wait_for_cars(driver, max_wait=8)
                
                # Screenshot
                driver.save_screenshot(f"{ss_dir}/cat_{cat_code}_{cat_name}.png")
                
                # Contar e extrair carros
                n_cars = count_cars(driver)
                cars = extract_cars_from_page(driver)
                
                all_cars[cat_code] = cars
                
                print(f"   ✅ {n_cars} carros encontrados ({len(cars)} extraídos)")
                
                for car in cars[:3]:
                    print(f"      - {car['name']} | {car['supplier']} | {car['price']}")
                if len(cars) > 3:
                    print(f"      ... e mais {len(cars) - 3} carros")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                driver.save_screenshot(f"{ss_dir}/erro_{cat_code}.png")
        
        # Deduplicação: juntar todos os carros, remover duplicados por nome+supplier
        print("\n" + "=" * 70)
        print("� DEDUPLICAÇÃO")
        print("=" * 70)
        
        seen = set()
        unique_cars = []
        total_before = 0
        
        for cat, cars in all_cars.items():
            total_before += len(cars)
            for car in cars:
                key = (car['name'].strip().lower(), car['supplier'].strip().lower())
                if key not in seen and car['name'].strip():
                    seen.add(key)
                    unique_cars.append({**car, 'category': cat})
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL")
        print("=" * 70)
        
        for cat, cars in all_cars.items():
            print(f"   {cat:10s}: {len(cars):3d} carros")
        
        print(f"\n   TOTAL BRUTO: {total_before} carros (com duplicados)")
        print(f"   TOTAL ÚNICO: {len(unique_cars)} carros (após deduplicação)")
        print(f"   DUPLICADOS REMOVIDOS: {total_before - len(unique_cars)}")
        print(f"   Screenshots em: {ss_dir}/")
        
        # Pausa para o utilizador ver
        print("\n" + "=" * 70)
        input("👀 Pressione ENTER para fechar o navegador...")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot(f"{ss_dir}/erro_fatal.png")
        input("\nPressione ENTER para fechar...")
    
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


if __name__ == '__main__':
    test_categories()
