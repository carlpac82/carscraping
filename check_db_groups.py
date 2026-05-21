#!/usr/bin/env python3
"""Verificar grupos na base de dados do último scraping"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from collections import Counter

print("\n" + "=" * 80)
print("ANÁLISE DE GRUPOS - ÚLTIMO SCRAPING NA BD")
print("=" * 80)

try:
    conn = get_db()
    cursor = conn.cursor()
    
    # Buscar último scraping
    cursor.execute("""
        SELECT 
            "group",
            car,
            category,
            transmission,
            price,
            supplier,
            created_at
        FROM carjet_prices
        WHERE pickup_date = '2026-06-07'
        AND location LIKE '%Faro%'
        ORDER BY created_at DESC
        LIMIT 1000
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("\n❌ Nenhum dado encontrado para Faro em 2026-06-07")
        cursor.close()
        conn.close()
        exit(1)
    
    print(f"\n✅ Encontrados {len(rows)} carros no último scraping")
    print(f"   Data do scraping: {rows[0][6]}")
    
    # Análise de grupos
    grupos = Counter()
    grupos_detalhes = {}
    
    for row in rows:
        group, car, category, transmission, price, supplier, created = row
        
        grupos[group] += 1
        
        if group not in grupos_detalhes:
            grupos_detalhes[group] = []
        
        grupos_detalhes[group].append({
            'car': car,
            'category': category,
            'transmission': transmission,
            'price': price,
            'supplier': supplier
        })
    
    # Mostrar distribuição
    print("\n" + "=" * 80)
    print("DISTRIBUIÇÃO POR GRUPO")
    print("=" * 80)
    print(f"\n📊 TOTAL: {len(rows)} carros em {len(grupos)} grupos")
    print("-" * 80)
    for group in sorted(grupos.keys()):
        count = grupos[group]
        print(f"{group:10} | {count:4} carros")
    
    # FOCO: M1 e M2
    print("\n\n" + "=" * 80)
    print("🎯 FOCO: 7 LUGARES (M1 vs M2)")
    print("=" * 80)
    
    m1_cars = grupos_detalhes.get('M1', [])
    m2_cars = grupos_detalhes.get('M2', [])
    
    print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
    print("-" * 80)
    for i, car in enumerate(m1_cars[:15], 1):
        print(f"{i:2}. {car['car'][:55]:55} | {car['transmission']:10} | {car['category'][:20]}")
    if len(m1_cars) > 15:
        print(f"... e mais {len(m1_cars) - 15}")
    
    print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
    print("-" * 80)
    if len(m2_cars) > 0:
        for i, car in enumerate(m2_cars[:15], 1):
            print(f"{i:2}. {car['car'][:55]:55} | {car['transmission']:10} | {car['category'][:20]}")
        if len(m2_cars) > 15:
            print(f"... e mais {len(m2_cars) - 15}")
    else:
        print("⚠️  NENHUM CARRO EM M2!")
    
    # DIAGNÓSTICO
    if len(m2_cars) < 5:
        print("\n\n" + "=" * 80)
        print("🔍 DIAGNÓSTICO: Carros 7 lugares automáticos em outros grupos")
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
                car_lower = car['car'].lower() if car['car'] else ''
                is_auto = 'automatic' in (car['transmission'] or '').lower()
                is_7_seater = any(m in car_lower for m in seven_seater_models)
                has_7 = '7' in (car.get('category') or '')
                
                if is_auto and (is_7_seater or has_7):
                    found.append({
                        'group': group,
                        'car': car['car'],
                        'transmission': car['transmission'],
                        'category': car['category']
                    })
        
        if found:
            print(f"\n❗ {len(found)} carros 7 lugares automáticos em grupos ERRADOS:\n")
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
                if len(by_group[g]) > 10:
                    print(f"  ... e mais {len(by_group[g]) - 10}")
        else:
            print("\n✅ Não encontrados carros 7 lugares automáticos mal classificados")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Análise concluída!")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
