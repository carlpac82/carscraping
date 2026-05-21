#!/usr/bin/env python3
"""Análise do scraping atual via API"""

import requests
import json
from collections import Counter

print("\n" + "=" * 80)
print("ANÁLISE DO SCRAPING ATUAL - VIA API")
print("=" * 80)

# Fazer pesquisa via API
url = "https://rentalprices.pt/api/track-by-params"
payload = {
    "location": "Aeroporto de Faro",
    "pickup_date": "2026-06-07",
    "days": 5
}

print(f"\n🔍 Fazendo scraping via API...")
print(f"   Local: {payload['location']}")
print(f"   Data: {payload['pickup_date']}")
print(f"   Dias: {payload['days']}")
print(f"\n⏳ Aguardando (pode demorar 1-2 minutos)...")

try:
    response = requests.post(url, json=payload, timeout=180)
    data = response.json()
    
    if 'items' not in data:
        print(f"\n❌ Resposta inesperada: {data}")
        exit(1)
    
    items = data['items']
    print(f"\n✅ Scraping concluído: {len(items)} carros encontrados")
    
    # Análise de grupos
    print("\n" + "=" * 80)
    print("DISTRIBUIÇÃO POR GRUPO")
    print("=" * 80)
    
    grupos = Counter()
    grupos_detalhes = {}
    
    for item in items:
        group = item.get('group', 'Unknown')
        grupos[group] += 1
        
        if group not in grupos_detalhes:
            grupos_detalhes[group] = []
        
        grupos_detalhes[group].append({
            'car': item.get('car', ''),
            'category': item.get('category', ''),
            'transmission': item.get('transmission', ''),
            'price': item.get('price', ''),
            'supplier': item.get('supplier', '')
        })
    
    # Mostrar distribuição
    print(f"\n📊 TOTAL: {len(items)} carros em {len(grupos)} grupos")
    print("-" * 80)
    for group in sorted(grupos.keys()):
        count = grupos[group]
        print(f"{group:10} | {count:4} carros")
    
    # FOCO: 7 LUGARES (M1 e M2)
    print("\n\n" + "=" * 80)
    print("🎯 ANÁLISE DETALHADA: 7 LUGARES (M1 vs M2)")
    print("=" * 80)
    
    m1_cars = grupos_detalhes.get('M1', [])
    m2_cars = grupos_detalhes.get('M2', [])
    
    print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
    print("-" * 80)
    for i, car in enumerate(m1_cars[:15], 1):
        print(f"{i:2}. {car['car'][:55]:55} | Trans: {car['transmission']:10} | Cat: {car['category'][:20]}")
    if len(m1_cars) > 15:
        print(f"... e mais {len(m1_cars) - 15} carros")
    
    print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
    print("-" * 80)
    if len(m2_cars) > 0:
        for i, car in enumerate(m2_cars[:15], 1):
            print(f"{i:2}. {car['car'][:55]:55} | Trans: {car['transmission']:10} | Cat: {car['category'][:20]}")
        if len(m2_cars) > 15:
            print(f"... e mais {len(m2_cars) - 15} carros")
    else:
        print("⚠️  NENHUM CARRO ENCONTRADO EM M2!")
    
    # DIAGNÓSTICO: Procurar carros 7 lugares automáticos mal classificados
    if len(m2_cars) < 5:  # Se M2 tem poucos ou nenhum carro
        print("\n\n" + "=" * 80)
        print("🔍 DIAGNÓSTICO: Procurando carros 7 lugares automáticos em OUTROS grupos")
        print("=" * 80)
        
        # Lista de modelos conhecidos de 7 lugares
        seven_seater_models = [
            'caddy', 'multivan', 'sharan', 'touran', 'alhambra',
            'galaxy', 's-max', 's max', 'grand scenic', 'c4 picasso', 
            'grand picasso', 'spacetourer', '5008', 'lodgy', 'jogger', 
            'rifter', 'zafira', 'combo', 'kodiaq', 'glb', 'v-class', 'v class'
        ]
        
        found_issues = []
        
        for group, cars in grupos_detalhes.items():
            if group == 'M2':
                continue
            
            for car in cars:
                car_lower = car['car'].lower()
                is_auto = 'automatic' in car['transmission'].lower()
                is_7_seater = any(model in car_lower for model in seven_seater_models)
                has_7_in_category = '7' in car.get('category', '')
                
                if is_auto and (is_7_seater or has_7_in_category):
                    found_issues.append({
                        'group': group,
                        'car': car['car'],
                        'transmission': car['transmission'],
                        'category': car['category'],
                        'supplier': car['supplier']
                    })
        
        if found_issues:
            print(f"\n❗ PROBLEMA ENCONTRADO: {len(found_issues)} carros 7 lugares automáticos em grupos ERRADOS:\n")
            
            # Agrupar por grupo incorreto
            by_wrong_group = {}
            for issue in found_issues:
                g = issue['group']
                if g not in by_wrong_group:
                    by_wrong_group[g] = []
                by_wrong_group[g].append(issue)
            
            for wrong_group in sorted(by_wrong_group.keys()):
                cars_in_wrong = by_wrong_group[wrong_group]
                print(f"Grupo {wrong_group} (deveria ser M2): {len(cars_in_wrong)} carros")
                print("-" * 80)
                for i, issue in enumerate(cars_in_wrong[:10], 1):
                    print(f"  {i:2}. {issue['car'][:60]:60}")
                    print(f"      Trans: {issue['transmission']:10} | Cat: {issue['category'][:30]:30} | Supplier: {issue['supplier']}")
                if len(cars_in_wrong) > 10:
                    print(f"  ... e mais {len(cars_in_wrong) - 10}")
                print()
        else:
            print("\n✅ Não foram encontrados carros 7 lugares automáticos mal classificados")
            print("   Possível causa: CarJet não tem estes carros nesta pesquisa específica")
    
    # Salvar para análise
    print("\n💾 Salvando resultados...")
    with open('scraping_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(items),
            'groups_distribution': dict(grupos),
            'M1_count': len(m1_cars),
            'M2_count': len(m2_cars),
            'M1_sample': m1_cars[:5],
            'M2_sample': m2_cars[:5] if m2_cars else [],
            'all_items': items
        }, f, indent=2, ensure_ascii=False)
    print("   → Salvo em scraping_analysis_results.json")
    
    print("\n✅ Análise concluída!")

except requests.exceptions.Timeout:
    print("\n❌ ERRO: Timeout - scraping demorou mais de 3 minutos")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
