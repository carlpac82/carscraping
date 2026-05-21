#!/usr/bin/env python3
"""Executar scraping usando o código do projeto (carjet_batch.py)"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from collections import Counter
import json

# Importar funções do projeto
from main import parse_prices, map_category_to_group
from carjet_batch import scrape_carjet_batch

print("\n" + "=" * 80)
print("SCRAPING TESTE - USANDO CÓDIGO DO PROJETO")
print("=" * 80)

# Configurar pesquisa
location = "Aeroporto de Faro"
pickup_date = datetime(2026, 6, 7, 15, 0)
searches = [{
    'days': 5,
    'start_dt': pickup_date,
    'end_dt': pickup_date + timedelta(days=5)
}]

print(f"\n🔍 Configuração:")
print(f"   Local: {location}")
print(f"   Data: {pickup_date.strftime('%Y-%m-%d')}")
print(f"   Dias: 5")
print(f"\n🚀 Iniciando scraping (pode demorar 2-3 minutos)...")

# Funções auxiliares simples
def convert_items_gbp_to_eur(items):
    return items

def apply_price_adjustments(items, url):
    return items

def normalize_and_sort(items, supplier_priority=None):
    return items

def filter_automatic_only(items):
    return items

try:
    # Executar scraping usando carjet_batch.py
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
    
    # Processar resultados
    all_items = []
    for day_items in results.values():
        all_items.extend(day_items)
    
    print(f"\n✅ Scraping concluído: {len(all_items)} carros encontrados")
    
    # Analisar grupos
    grupos = Counter()
    grupos_detalhes = {}
    
    for item in all_items:
        group = item.get('group', 'Unknown')
        grupos[group] += 1
        
        if group not in grupos_detalhes:
            grupos_detalhes[group] = []
        
        grupos_detalhes[group].append(item)
    
    # Mostrar distribuição
    print("\n" + "=" * 80)
    print("DISTRIBUIÇÃO POR GRUPO")
    print("=" * 80)
    for g in sorted(grupos.keys()):
        print(f"{g:10} | {grupos[g]:4} carros")
    
    # Análise M1 vs M2
    print("\n\n" + "=" * 80)
    print("🎯 ANÁLISE: 7 LUGARES (M1 vs M2)")
    print("=" * 80)
    
    m1_cars = grupos_detalhes.get('M1', [])
    m2_cars = grupos_detalhes.get('M2', [])
    
    print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
    for i, car in enumerate(m1_cars[:10], 1):
        print(f"  {i:2}. {car.get('car', '')[:60]:60} | {car.get('transmission', ''):10}")
    if len(m1_cars) > 10:
        print(f"  ... e mais {len(m1_cars) - 10}")
    
    print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
    if len(m2_cars) > 0:
        for i, car in enumerate(m2_cars[:10], 1):
            print(f"  {i:2}. {car.get('car', '')[:60]:60} | {car.get('transmission', ''):10}")
        if len(m2_cars) > 10:
            print(f"  ... e mais {len(m2_cars) - 10}")
    else:
        print("  ⚠️  NENHUM CARRO EM M2!")
    
    # Diagnóstico
    if len(m2_cars) < 5:
        print("\n\n" + "=" * 80)
        print("🔍 DIAGNÓSTICO: Procurando 7 lugares automáticos mal classificados")
        print("=" * 80)
        
        models = ['caddy', 'multivan', 'sharan', 'touran', 'alhambra', 'galaxy', 
                 's-max', 's max', 'grand scenic', 'c4 picasso', 'grand picasso', 
                 'spacetourer', '5008', 'lodgy', 'jogger', 'rifter', 'zafira', 
                 'combo', 'kodiaq', 'glb', 'v-class', 'v class']
        
        found_by_group = {}
        for group, items in grupos_detalhes.items():
            if group == 'M2':
                continue
            
            for item in items:
                car = item.get('car', '').lower()
                trans = item.get('transmission', '').lower()
                
                if 'automatic' in trans and any(m in car for m in models):
                    if group not in found_by_group:
                        found_by_group[group] = []
                    found_by_group[group].append(item)
        
        if found_by_group:
            total_misplaced = sum(len(v) for v in found_by_group.values())
            print(f"\n❗ PROBLEMA ENCONTRADO: {total_misplaced} carros 7 lugares automáticos em grupos ERRADOS:\n")
            
            for g in sorted(found_by_group.keys()):
                items = found_by_group[g]
                print(f"\nGrupo {g} (deveria ser M2): {len(items)} carros")
                print("-" * 80)
                for i, item in enumerate(items[:10], 1):
                    print(f"  {i:2}. {item.get('car', '')[:65]:65}")
                    print(f"      Trans: {item.get('transmission', ''):10} | Cat: {item.get('category', '')}")
                if len(items) > 10:
                    print(f"  ... e mais {len(items) - 10}")
        else:
            print("\n✅ Não encontrados carros 7 lugares automáticos mal classificados")
    
    # Salvar resultados
    print("\n\n💾 Salvando resultados...")
    with open('scraping_test_final.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(all_items),
            'groups_distribution': dict(grupos),
            'M1_count': len(m1_cars),
            'M2_count': len(m2_cars),
            'all_items': all_items
        }, f, indent=2, ensure_ascii=False)
    print("   → Salvo em scraping_test_final.json")
    
    print("\n✅ Análise concluída!")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
