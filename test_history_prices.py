#!/usr/bin/env python3
"""
Testa os dados do histórico para identificar onde os preços são multiplicados por 100
"""
import psycopg2
import json

RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🔍 TESTE DE DADOS DO HISTÓRICO')
print('=' * 70)

conn = psycopg2.connect(RAILWAY_DB_URL)
cur = conn.cursor()

# Obter a pesquisa mais recente
cur.execute('''
    SELECT id, location, start_date, days, results_data, created_at
    FROM recent_searches
    WHERE results_data IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 1
''')

row = cur.fetchone()

if row:
    print(f'\nPesquisa ID: {row[0]}')
    print(f'Location: {row[1]}')
    print(f'Created: {row[5]}')
    
    results = json.loads(row[4])
    
    # Agrupar por supplier
    by_supplier = {}
    for car in results:
        supplier = car.get('supplier', 'Unknown')
        if supplier not in by_supplier:
            by_supplier[supplier] = []
        by_supplier[supplier].append(car)
    
    print(f'\n📊 ANÁLISE DE PREÇOS POR SUPPLIER:')
    print(f'Total de suppliers: {len(by_supplier)}')
    
    # Mostrar primeiros 3 carros de cada supplier
    for supplier in sorted(by_supplier.keys())[:10]:
        cars = by_supplier[supplier]
        print(f'\n  {supplier} ({len(cars)} carros):')
        for car in cars[:3]:
            price = car.get('price_num', 0)
            print(f'    - {car.get("car", "N/A")}: {price}€ (tipo: {type(price).__name__})')
    
    # Verificar se há preços > 1000 (suspeitos)
    high_prices = [c for c in results if c.get('price_num', 0) > 1000]
    if high_prices:
        print(f'\n⚠️  PREÇOS SUSPEITOS (> 1000€): {len(high_prices)} carros')
        for car in high_prices[:5]:
            print(f'    - {car.get("car", "N/A")} - {car.get("supplier", "N/A")}: {car.get("price_num", 0)}€')
    
    # Verificar se há preços < 10 (normais)
    low_prices = [c for c in results if 0 < c.get('price_num', 0) < 10]
    if low_prices:
        print(f'\n✅ PREÇOS NORMAIS (< 10€): {len(low_prices)} carros')
        for car in low_prices[:5]:
            print(f'    - {car.get("car", "N/A")} - {car.get("supplier", "N/A")}: {car.get("price_num", 0)}€')

cur.close()
conn.close()

print('\n' + '=' * 70)
print('✅ Teste concluído')
