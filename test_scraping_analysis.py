#!/usr/bin/env python3
"""Teste de scraping com análise detalhada"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import parse_prices, map_category_to_group
import requests
from bs4 import BeautifulSoup
from collections import Counter
import json

print("\n" + "=" * 80)
print("TESTE DE SCRAPING E PARSING - ANÁLISE DETALHADA")
print("=" * 80)

# URL de teste CarJet
url = "https://www.carjet.com/do/list/pt"
params = {
    "fecRec": "2026-06-07",
    "fecDev": "2026-06-12",
    "horRec": "10:00",
    "horDev": "10:00",
    "lugRec": "Faro Aeroporto (FAO)",
    "lugDev": "Faro Aeroporto (FAO)",
    "edad": "30"
}

print(f"\n🔍 Fazendo request para CarJet...")
print(f"   Pickup: {params['fecRec']} | Return: {params['fecDev']}")
print(f"   Local: {params['lugRec']}")

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=30)
    html = response.text
    
    print(f"✅ HTML recebido: {len(html)} bytes")
    
    # Parse com a função do main.py
    print(f"\n📊 Fazendo parse com parse_prices()...")
    items = parse_prices(html, url)
    
    print(f"✅ Parse concluído: {len(items)} carros encontrados")
    
    if len(items) == 0:
        print("\n❌ ERRO: Nenhum carro encontrado!")
        print("   Salvando HTML para debug...")
        with open('debug_carjet.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   → Salvo em debug_carjet.html")
        sys.exit(1)
    
    # Análise de grupos
    print("\n" + "=" * 80)
    print("ANÁLISE DE GRUPOS")
    print("=" * 80)
    
    grupos = Counter()
    grupos_detalhes = {}
    
    for item in items:
        car = item.get('car', '')
        category = item.get('category', '')
        transmission = item.get('transmission', '')
        
        # Mapear para grupo
        group = map_category_to_group(category, car, transmission)
        grupos[group] += 1
        
        if group not in grupos_detalhes:
            grupos_detalhes[group] = []
        
        grupos_detalhes[group].append({
            'car': car,
            'category': category,
            'transmission': transmission,
            'price': item.get('price', 'N/A')
        })
    
    # Mostrar distribuição
    print(f"\n📊 DISTRIBUIÇÃO POR GRUPO ({len(items)} carros):")
    print("-" * 80)
    for group in sorted(grupos.keys()):
        count = grupos[group]
        print(f"{group:10} | {count:4} carros")
    
    # Foco em 7 Lugares (M1 e M2)
    print("\n\n🎯 ANÁLISE DETALHADA: 7 LUGARES (M1 e M2)")
    print("=" * 80)
    
    m1_cars = grupos_detalhes.get('M1', [])
    m2_cars = grupos_detalhes.get('M2', [])
    
    print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
    for i, car in enumerate(m1_cars[:10], 1):
        print(f"  {i}. {car['car'][:60]:60} | Trans: {car['transmission']:10} | Cat: {car['category']}")
    if len(m1_cars) > 10:
        print(f"  ... e mais {len(m1_cars) - 10} carros")
    
    print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
    for i, car in enumerate(m2_cars[:10], 1):
        print(f"  {i}. {car['car'][:60]:60} | Trans: {car['transmission']:10} | Cat: {car['category']}")
    if len(m2_cars) > 10:
        print(f"  ... e mais {len(m2_cars) - 10} carros")
    
    # DIAGNÓSTICO: Procurar carros 7 lugares automáticos em outros grupos
    if len(m2_cars) == 0:
        print("\n\n⚠️  PROBLEMA DETECTADO: M2 está vazio!")
        print("=" * 80)
        print("Procurando carros 7 lugares automáticos em OUTROS grupos...\n")
        
        found_misplaced = False
        for group, cars in grupos_detalhes.items():
            if group != 'M2':
                # Procurar carros com transmissão automática E categoria/nome com "7"
                auto_7_seaters = []
                for c in cars:
                    is_auto = 'Automatic' in c.get('transmission', '')
                    has_7 = '7' in c.get('category', '') or '7' in c.get('car', '')
                    
                    # Ou verificar nomes específicos de 7 lugares
                    car_lower = c.get('car', '').lower()
                    is_7_seater_model = any(model in car_lower for model in [
                        'caddy', 'multivan', 'sharan', 'touran', 'alhambra',
                        'galaxy', 's-max', 'grand scenic', 'c4 picasso', 
                        'grand picasso', '5008', 'lodgy', 'jogger', 'rifter',
                        'zafira', 'combo', 'kodiaq', 'glb', 'v-class', 'v class'
                    ])
                    
                    if is_auto and (has_7 or is_7_seater_model):
                        auto_7_seaters.append(c)
                
                if auto_7_seaters:
                    found_misplaced = True
                    print(f"❗ Grupo {group}: {len(auto_7_seaters)} carros 7 lugares automáticos")
                    for c in auto_7_seaters[:5]:
                        print(f"   - {c['car'][:65]:65} | Trans: {c['transmission']}")
                    if len(auto_7_seaters) > 5:
                        print(f"   ... e mais {len(auto_7_seaters) - 5}")
                    print()
        
        if not found_misplaced:
            print("✅ Não foram encontrados carros 7 lugares automáticos em outros grupos")
            print("   Possíveis causas:")
            print("   1. CarJet não tem carros 7 lugares automáticos nesta pesquisa")
            print("   2. Transmissão não está a ser detectada corretamente")
    
    # Salvar resultados para análise
    print("\n\n💾 Salvando resultados...")
    with open('test_scraping_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_cars': len(items),
            'groups_distribution': dict(grupos),
            'items': items[:50]  # Primeiros 50 para análise
        }, f, indent=2, ensure_ascii=False)
    print("   → Salvo em test_scraping_results.json")
    
    print("\n✅ Análise concluída!")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
