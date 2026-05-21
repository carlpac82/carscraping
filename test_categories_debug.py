#!/usr/bin/env python3
"""Testar navegação de categorias com debug"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import time
import platform

CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']

print("\n" + "=" * 80)
print("TESTE DEBUG - NAVEGAÇÃO DE CATEGORIAS")
print("=" * 80)

# Setup Chrome como iPhone (igual ao carjet_batch.py)
iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1"

chrome_options = Options()
system = platform.system()

if system != 'Linux':
    print(f"[DEBUG] Modo visual ({system})")
else:
    chrome_options.add_argument('--headless=new')

chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(f'user-agent={iphone_ua}')
chrome_options.add_argument('--window-size=390,844')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

mobile_emulation = {
    "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
    "userAgent": iphone_ua
}
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

print("\n🚀 Iniciando Chrome...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Aplicar stealth
stealth(driver,
    languages=["pt-PT", "pt", "en-US", "en"],
    vendor="Apple Computer, Inc.",
    platform="iPhone",
    webgl_vendor="Apple Inc.",
    renderer="Apple GPU",
    fix_hairline=True,
)

try:
    # Ir para CarJet e fazer pesquisa
    print("\n📍 Navegando para CarJet...")
    driver.get("https://www.carjet.com/aluguel-carros/index.htm")
    time.sleep(3)
    
    # Cookies
    try:
        driver.execute_script("document.querySelector('#didomi-notice-agree-button')?.click();")
        time.sleep(1)
    except:
        pass
    
    # Preencher pesquisa
    print("\n📝 Preenchendo pesquisa (Faro, 07/06 → 12/06)...")
    driver.execute_script("""
        document.querySelector('#txtDestino').value = 'Faro';
        document.querySelector('#txtFecRec').value = '07/06/2026';
        document.querySelector('#txtFecDev').value = '12/06/2026';
    """)
    time.sleep(1)
    
    # Submeter
    print("🔍 Submetendo...")
    driver.execute_script("document.querySelector('#btnBuscar')?.click();")
    time.sleep(15)
    
    print("\n" + "=" * 80)
    print("TESTANDO NAVEGAÇÃO POR CATEGORIAS")
    print("=" * 80)
    
    results = {}
    
    for cat in CATEGORIES:
        print(f"\n📂 Categoria: {cat}")
        
        # Executar filterAgrupVeh
        result = driver.execute_script(f"""
            try {{
                filterAgrupVeh('{cat}');
                return 'ok';
            }} catch(e) {{
                return 'error: ' + e.message;
            }}
        """)
        print(f"   filterAgrupVeh('{cat}'): {result}")
        
        # Aguardar estabilizar
        time.sleep(3)
        
        # Contar artigos
        count = driver.execute_script("return document.querySelectorAll('article').length") or 0
        print(f"   Artigos encontrados: {count}")
        
        # Verificar se há carros com "Auto" no nome
        auto_cars = driver.execute_script("""
            const articles = document.querySelectorAll('article');
            let autoCount = 0;
            let examples = [];
            articles.forEach(art => {
                const name = art.querySelector('h2, .car-name, [class*="name"]')?.textContent || '';
                if (name.toLowerCase().includes('auto')) {
                    autoCount++;
                    if (examples.length < 3) {
                        examples.push(name.trim());
                    }
                }
            });
            return {count: autoCount, examples: examples};
        """)
        
        print(f"   Carros com 'Auto' no nome: {auto_cars['count']}")
        if auto_cars['examples']:
            for ex in auto_cars['examples']:
                print(f"      - {ex}")
        
        results[cat] = {
            'total': count,
            'auto_count': auto_cars['count'],
            'examples': auto_cars['examples']
        }
    
    # Resumo
    print("\n\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    for cat in CATEGORIES:
        data = results.get(cat, {})
        total = data.get('total', 0)
        auto_count = data.get('auto_count', 0)
        print(f"{cat:10} | Total: {total:3} | Com 'Auto': {auto_count:3}")
    
    print("\n\n✅ Teste concluído!")
    print("   Pressione ENTER para fechar Chrome...")
    input()

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    input("\nPressione ENTER para fechar...")
finally:
    driver.quit()
    print("\n👋 Chrome fechado")
