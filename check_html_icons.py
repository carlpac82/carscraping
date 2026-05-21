#!/usr/bin/env python3
"""Verificar se HTML do scraping contém ícones de transmissão"""

import sys
import os
sys.path.insert(0, os.getcwd())

from datetime import datetime, timedelta
from carjet_batch import scrape_carjet_batch
from main import parse_prices

# Modificar temporariamente scrape_carjet_batch para salvar HTML
import carjet_batch

original_navigate = carjet_batch._navigate_categories

saved_html = []

def _navigate_with_save(driver, batch_id=None):
    global saved_html
    result = original_navigate(driver, batch_id)
    saved_html = result
    return result

carjet_batch._navigate_categories = _navigate_with_save

print("\n" + "=" * 80)
print("VERIFICAR ÍCONES DE TRANSMISSÃO NO HTML")
print("=" * 80)

def convert_items_gbp_to_eur(items):
    return items

def apply_price_adjustments(items, url):
    return items

def normalize_and_sort(items, supplier_priority=None):
    return items

def filter_automatic_only(items):
    return items

location = 'Aeroporto de Faro'
pickup_date = datetime(2026, 6, 7, 15, 0)
searches = [{
    'days': 5,
    'start_dt': pickup_date,
    'end_dt': pickup_date + timedelta(days=5)
}]

print(f"\n🔍 Fazendo scraping...")
results = scrape_carjet_batch(
    location=location,
    searches=searches,
    parse_prices_fn=parse_prices,
    convert_fn=convert_items_gbp_to_eur,
    adjust_fn=apply_price_adjustments,
    normalize_fn=normalize_and_sort,
    filter_fn=filter_automatic_only,
    lang='pt',
    currency='EUR'
)

print(f"\n✅ Scraping concluído")
print(f"📄 HTML parts capturados: {len(saved_html)}")

# Analisar HTML
from bs4 import BeautifulSoup

for i, html_part in enumerate(saved_html):
    print(f"\n{'=' * 80}")
    print(f"CATEGORIA {i+1}/{len(saved_html)}")
    print(f"{'=' * 80}")
    
    # Salvar HTML
    filename = f'html_categoria_{i+1}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_part)
    print(f"💾 Salvo em {filename}")
    
    # Procurar ícones
    count_icon_transm_auto = html_part.count('icon-transm-auto')
    count_icon_transm = html_part.count('icon-transm')
    count_articles = html_part.count('<article')
    
    print(f"\n📊 Estatísticas:")
    print(f"   Articles: {count_articles}")
    print(f"   icon-transm (total): {count_icon_transm}")
    print(f"   icon-transm-auto: {count_icon_transm_auto}")
    
    if count_icon_transm_auto > 0:
        print(f"\n✅ ENCONTROU {count_icon_transm_auto} ícones automáticos!")
    else:
        print(f"\n❌ NÃO encontrou ícones automáticos")
    
    # Procurar por "Auto" nos nomes
    soup = BeautifulSoup(html_part, 'lxml')
    h2_elements = soup.find_all('h2')
    
    auto_in_names = [h2.get_text(strip=True) for h2 in h2_elements if 'auto' in h2.get_text(strip=True).lower()]
    
    print(f"\n🚗 H2 com 'Auto' no nome: {len(auto_in_names)}")
    if auto_in_names:
        for name in auto_in_names[:5]:
            print(f"   - {name}")

print("\n\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)

total_auto_icons = sum(html.count('icon-transm-auto') for html in saved_html)
total_articles = sum(html.count('<article') for html in saved_html)

print(f"Total de articles: {total_articles}")
print(f"Total de ícones automáticos: {total_auto_icons}")

if total_auto_icons == 0:
    print("\n❌ PROBLEMA: Nenhum ícone de transmissão automática encontrado!")
    print("   Isto explica porque todos os carros foram classificados como Manual (M1)")
else:
    print(f"\n✅ Encontrados {total_auto_icons} ícones automáticos")
    print("   O problema pode estar no parsing, não no scraping")

print("\n✅ Análise concluída!")
