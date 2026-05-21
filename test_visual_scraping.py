#!/usr/bin/env python3
"""Teste VISUAL com Chrome - ver scraping em tempo real"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from collections import Counter

print("\n" + "=" * 80)
print("TESTE VISUAL - SCRAPING CARJET")
print("=" * 80)

# Chrome em modo VISÍVEL
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

print("\n🚀 Iniciando Chrome (modo visual)...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Ir para homepage do CarJet
    print(f"\n📍 Navegando para CarJet homepage...")
    driver.get("https://www.carjet.com/pt/")
    
    print("⏳ Aguardando homepage carregar...")
    time.sleep(5)
    
    # Aceitar cookies
    try:
        print("\n🍪 Tentando aceitar cookies...")
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        cookie_btn.click()
        print("✅ Cookies aceites")
        time.sleep(2)
    except:
        print("⚠️  Sem banner de cookies")
    
    # Preencher formulário de pesquisa
    print("\n📝 Preenchendo formulário...")
    
    # Local
    print("   Local: Faro Aeroporto (FAO)")
    location_input = driver.find_element(By.ID, "txtDestino")
    location_input.clear()
    location_input.send_keys("Faro Aeroporto (FAO)")
    time.sleep(2)
    
    # Selecionar da lista
    try:
        faro_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Faro')]"))
        )
        faro_option.click()
        time.sleep(1)
    except:
        print("   ⚠️  Não conseguiu selecionar Faro da lista")
    
    # Data pickup
    print("   Data: 07/06/2026")
    pickup_date = driver.find_element(By.ID, "txtFecRec")
    pickup_date.clear()
    pickup_date.send_keys("07/06/2026")
    time.sleep(1)
    
    # Data devolução
    print("   Devolução: 12/06/2026 (5 dias)")
    return_date = driver.find_element(By.ID, "txtFecDev")
    return_date.clear()
    return_date.send_keys("12/06/2026")
    time.sleep(1)
    
    # Submeter pesquisa
    print("\n🔍 Submetendo pesquisa...")
    search_btn = driver.find_element(By.ID, "btnBuscar")
    search_btn.click()
    
    print("⏳ Aguardando resultados (30 segundos)...")
    time.sleep(30)
    
    # Contar carros por categoria
    print("\n" + "=" * 80)
    print("NAVEGANDO PELAS CATEGORIAS")
    print("=" * 80)
    
    categories = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']
    results_by_category = {}
    
    for category in categories:
        try:
            print(f"\n📂 Categoria: {category}")
            
            # Clicar na categoria
            cat_button = driver.find_element(By.XPATH, f"//button[contains(text(), '{category}')]")
            cat_button.click()
            time.sleep(3)
            
            # Contar carros
            cars = driver.find_elements(By.CSS_SELECTOR, "section.newcarlist article")
            print(f"   ✅ Encontrados: {len(cars)} carros")
            
            # Mostrar primeiros 3
            if len(cars) > 0:
                print(f"   Primeiros 3 carros:")
                for i, car in enumerate(cars[:3], 1):
                    try:
                        name = car.find_element(By.CSS_SELECTOR, "h2, .car-name, [class*='name']").text
                        print(f"      {i}. {name}")
                    except:
                        print(f"      {i}. [Erro ao extrair nome]")
            
            results_by_category[category] = len(cars)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results_by_category[category] = 0
    
    # Resumo
    print("\n\n" + "=" * 80)
    print("RESUMO POR CATEGORIA")
    print("=" * 80)
    total = 0
    for cat in categories:
        count = results_by_category.get(cat, 0)
        total += count
        print(f"{cat:10} | {count:4} carros")
    
    print(f"\n{'TOTAL':10} | {total:4} carros")
    
    # Foco em AUTO
    auto_count = results_by_category.get('AUTO', 0)
    print(f"\n\n🎯 CATEGORIA AUTO: {auto_count} carros")
    
    if auto_count > 0:
        print("\n⚠️  IMPORTANTE: Estes carros deveriam ser mapeados para grupos automáticos:")
        print("   - Mini Auto → E1")
        print("   - Economy Auto → E2")
        print("   - SUV Auto → L1")
        print("   - Station Wagon Auto → L2")
        print("   - 7 Seater Auto → M2")
    
    print("\n\n✅ Teste concluído!")
    print("   A janela do Chrome ficará aberta para inspeção.")
    print("   Pressione ENTER para fechar...")
    
    input()
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    input("\nPressione ENTER para fechar...")
finally:
    driver.quit()
    print("\n👋 Chrome fechado")
