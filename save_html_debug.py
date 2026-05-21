#!/usr/bin/env python3
"""Salvar HTML bruto do scraping para debug"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import time
import platform

print("\n" + "=" * 80)
print("SALVAR HTML BRUTO DO SCRAPING")
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
    print("\n📝 Preenchendo pesquisa (Faro, 06/06 → 11/06)...")
    driver.execute_script("""
        document.querySelector('#txtDestino').value = 'Faro';
        document.querySelector('#txtFecRec').value = '06/06/2026';
        document.querySelector('#txtFecDev').value = '11/06/2026';
    """)
    time.sleep(1)
    
    # Submeter
    print("🔍 Submetendo...")
    driver.execute_script("document.querySelector('#btnBuscar')?.click();")
    time.sleep(15)
    html = result['html']
    
    # Salvar HTML
    with open('/tmp/carjet_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML salvo: /tmp/carjet_debug.html ({len(html)} bytes)")
    
    # Procurar por ícones de transmissão
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    
    # Procurar todos os ícones
    all_icons = soup.find_all('i', class_=lambda x: x and 'icon' in x)
    print(f"\n📊 Total de ícones <i> encontrados: {len(all_icons)}")
    
    # Procurar especificamente transmissão
    trans_icons = soup.find_all('i', class_=lambda x: x and 'transm' in x)
    print(f"🔧 Ícones de transmissão: {len(trans_icons)}")
    
    if trans_icons:
        print("\n🔍 Exemplos de ícones de transmissão encontrados:")
        for icon in trans_icons[:5]:
            classes = ' '.join(icon.get('class', []))
            print(f"   - <i class=\"{classes}\">")
    else:
        print("\n⚠️  NENHUM ícone de transmissão encontrado!")
        print("\nVou procurar por 'manual' ou 'automatic' no HTML...")
        
        # Procurar texto
        if 'manual' in html.lower():
            print("✅ Palavra 'manual' encontrada no HTML")
        if 'automatic' in html.lower() or 'automático' in html.lower():
            print("✅ Palavra 'automatic' encontrada no HTML")
    
    # Procurar cards de carros
    cards = soup.find_all('article', class_=lambda x: x and 'card' in x)
    if not cards:
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x)
    
    print(f"\n🚗 Cards de carros encontrados: {len(cards)}")
    
    if cards:
        print("\n🔍 Analisando primeiro card:")
        first_card = cards[0]
        print(f"Classes do card: {first_card.get('class', [])}")
        print(f"HTML do card (primeiros 500 chars):")
        print(str(first_card)[:500])
        
else:
    print(f"❌ Erro: {result.get('error')}")
