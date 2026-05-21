#!/usr/bin/env python3
"""Verificar nomes dos carros no scraping"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from carjet_batch import scrape_carjet_batch
from main import parse_prices

print("\n" + "=" * 80)
print("VERIFICAR NOMES DOS CARROS")
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

all_items = []
for items in results.values():
    all_items.extend(items)

print(f"\n✅ Total: {len(all_items)} carros")

# Procurar carros com "auto" no nome
print("\n" + "=" * 80)
print("CARROS COM 'AUTO' NO NOME")
print("=" * 80)

auto_in_name = [item for item in all_items if 'auto' in item.get('car', '').lower()]
print(f"\nEncontrados: {len(auto_in_name)} carros")

if auto_in_name:
    print("\nPrimeiros 20:")
    for i, item in enumerate(auto_in_name[:20], 1):
        car = item.get('car', '')
        trans = item.get('transmission', '')
        group = item.get('group', '')
        cat = item.get('category', '')
        print(f"{i:2}. {car[:60]:60} | Trans: {trans:10} | Grupo: {group:3} | Cat: {cat[:20]}")

# Procurar carros 7 lugares
print("\n\n" + "=" * 80)
print("CARROS 7 LUGARES")
print("=" * 80)

seven_seater_models = ['caddy', 'multivan', 'sharan', 'touran', 'alhambra', 'galaxy', 
                       's-max', 's max', 'grand scenic', 'c4 picasso', 'grand picasso', 
                       'spacetourer', '5008', 'lodgy', 'jogger', 'rifter', 'zafira', 
                       'combo', 'kodiaq', 'glb', 'v-class', 'v class']

seven_seaters = []
for item in all_items:
    car = item.get('car', '').lower()
    cat = item.get('category', '').lower()
    
    if '7' in cat or any(model in car for model in seven_seater_models):
        seven_seaters.append(item)

print(f"\nEncontrados: {len(seven_seaters)} carros")

if seven_seaters:
    print("\nPrimeiros 30:")
    for i, item in enumerate(seven_seaters[:30], 1):
        car = item.get('car', '')
        trans = item.get('transmission', '')
        group = item.get('group', '')
        cat = item.get('category', '')
        has_auto = '✅' if 'auto' in car.lower() else '❌'
        print(f"{i:2}. {car[:55]:55} | {trans:10} | {group:3} | Auto no nome: {has_auto}")

print("\n✅ Análise concluída!")
