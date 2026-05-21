#!/usr/bin/env python3
"""Teste simples - fazer scraping e ver resultados"""

import requests
import json
from collections import Counter

print("\n" + "=" * 80)
print("TESTE: Fazer scraping e analisar grupos")
print("=" * 80)

# Fazer scraping via API (modo async)
url = "https://rentalprices.pt/api/track-by-params-batch"
payload = {
    "location": "Aeroporto de Faro",
    "pickup_date": "2026-06-07",
    "days": [5],
    "async": True
}

print(f"\n🔍 Iniciando scraping...")
print(f"   Local: {payload['location']}")
print(f"   Data: {payload['pickup_date']}")
print(f"   Dias: {payload['days']}")

try:
    # Iniciar batch
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()
    
    if not data.get('ok'):
        print(f"\n❌ Erro ao iniciar: {data}")
        exit(1)
    
    batch_id = data.get('batch_id')
    print(f"\n✅ Batch iniciado: {batch_id}")
    print(f"   Total de pesquisas: {data.get('total')}")
    
    # Polling para resultados
    import time
    max_wait = 180  # 3 minutos
    start_time = time.time()
    
    print(f"\n⏳ Aguardando resultados (máx {max_wait}s)...")
    
    while time.time() - start_time < max_wait:
        time.sleep(3)
        
        progress_url = f"https://rentalprices.pt/api/track-by-params-batch/progress/{batch_id}"
        prog_response = requests.get(progress_url, timeout=10)
        prog_data = prog_response.json()
        
        if not prog_data.get('ok'):
            print(f"\n❌ Erro ao obter progresso: {prog_data}")
            break
        
        status = prog_data.get('status')
        completed = prog_data.get('completed', 0)
        total = prog_data.get('total', 0)
        
        print(f"   Status: {status} | Progresso: {completed}/{total}", end='\r')
        
        if status == 'done':
            print(f"\n✅ Scraping concluído!")
            results = prog_data.get('results', {})
            
            # Analisar resultados
            all_items = []
            for day_key, items in results.items():
                all_items.extend(items)
            
            print(f"\n📊 Total de carros: {len(all_items)}")
            
            if len(all_items) == 0:
                print("\n❌ Nenhum carro encontrado!")
                exit(1)
            
            # Contar por grupo
            grupos = Counter()
            grupos_detalhes = {}
            
            for item in all_items:
                group = item.get('group', 'Unknown')
                grupos[group] += 1
                
                if group not in grupos_detalhes:
                    grupos_detalhes[group] = []
                
                grupos_detalhes[group].append({
                    'car': item.get('car', ''),
                    'category': item.get('category', ''),
                    'transmission': item.get('transmission', ''),
                    'price': item.get('price', '')
                })
            
            # Mostrar distribuição
            print("\n" + "=" * 80)
            print("DISTRIBUIÇÃO POR GRUPO")
            print("=" * 80)
            for group in sorted(grupos.keys()):
                count = grupos[group]
                print(f"{group:10} | {count:4} carros")
            
            # FOCO: M1 e M2
            print("\n\n" + "=" * 80)
            print("🎯 ANÁLISE: 7 LUGARES (M1 vs M2)")
            print("=" * 80)
            
            m1_cars = grupos_detalhes.get('M1', [])
            m2_cars = grupos_detalhes.get('M2', [])
            
            print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
            for i, car in enumerate(m1_cars[:10], 1):
                print(f"  {i:2}. {car['car'][:60]:60} | {car['transmission']:10}")
            
            print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
            if len(m2_cars) > 0:
                for i, car in enumerate(m2_cars[:10], 1):
                    print(f"  {i:2}. {car['car'][:60]:60} | {car['transmission']:10}")
            else:
                print("  ⚠️  NENHUM CARRO EM M2!")
            
            # Procurar carros 7 lugares automáticos em outros grupos
            if len(m2_cars) < 5:
                print("\n\n" + "=" * 80)
                print("🔍 PROCURANDO CARROS 7 LUGARES AUTOMÁTICOS EM OUTROS GRUPOS")
                print("=" * 80)
                
                seven_seater_models = [
                    'caddy', 'multivan', 'sharan', 'touran', 'alhambra',
                    'galaxy', 's-max', 's max', 'grand scenic', 'c4 picasso', 
                    'grand picasso', 'spacetourer', '5008', 'lodgy', 'jogger', 
                    'rifter', 'zafira', 'combo', 'kodiaq', 'glb', 'v-class', 'v class'
                ]
                
                found = []
                for group, cars in grupos_detalhes.items():
                    if group == 'M2':
                        continue
                    
                    for car in cars:
                        car_lower = car['car'].lower()
                        is_auto = 'automatic' in car['transmission'].lower()
                        is_7_seater = any(m in car_lower for m in seven_seater_models)
                        
                        if is_auto and is_7_seater:
                            found.append({
                                'group': group,
                                'car': car['car'],
                                'transmission': car['transmission'],
                                'category': car['category']
                            })
                
                if found:
                    print(f"\n❗ PROBLEMA: {len(found)} carros 7 lugares automáticos em grupos ERRADOS:\n")
                    
                    by_group = {}
                    for f in found:
                        g = f['group']
                        if g not in by_group:
                            by_group[g] = []
                        by_group[g].append(f)
                    
                    for g in sorted(by_group.keys()):
                        print(f"\nGrupo {g} (deveria ser M2): {len(by_group[g])} carros")
                        print("-" * 80)
                        for i, c in enumerate(by_group[g][:10], 1):
                            print(f"  {i:2}. {c['car'][:65]:65}")
                            print(f"      Trans: {c['transmission']:10} | Cat: {c['category']}")
                else:
                    print("\n✅ Não encontrados carros 7 lugares automáticos mal classificados")
            
            # Salvar resultados
            print("\n\n💾 Salvando resultados em scraping_test_results.json...")
            with open('scraping_test_results.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(all_items),
                    'groups_distribution': dict(grupos),
                    'M1_count': len(m1_cars),
                    'M2_count': len(m2_cars),
                    'all_items': all_items
                }, f, indent=2, ensure_ascii=False)
            
            print("✅ Análise concluída!")
            break
        
        elif status == 'error':
            print(f"\n❌ Erro no scraping: {prog_data.get('error')}")
            break
    
    else:
        print(f"\n⏱️ Timeout após {max_wait}s")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
