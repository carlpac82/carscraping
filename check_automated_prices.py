#!/usr/bin/env python3
import psycopg2
import sys
from datetime import datetime, timedelta

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'automated_prices'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("=== ESTRUTURA DA TABELA automated_prices ===")
    for col in columns:
        print(f"  {col[0]:<30} {col[1]}")
    
    # Verificar últimas atualizações
    cursor.execute("""
        SELECT 
            location,
            pickup_date,
            days,
            COUNT(*) as total_cars,
            MAX(last_updated) as last_update
        FROM automated_prices
        GROUP BY location, pickup_date, days
        ORDER BY last_update DESC NULLS LAST
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    
    print("\n=== ÚLTIMAS ATUALIZAÇÕES EM automated_prices ===")
    print(f"{'Location':<30} {'Data':<12} {'Dias':<6} {'Carros':<8} {'Última Atualização'}")
    print("-" * 90)
    
    if results:
        for row in results:
            location, pickup_date, days, total_cars, last_update = row
            print(f"{location:<30} {pickup_date} {days:<6} {total_cars:<8} {last_update}")
    else:
        print("❌ Nenhum dado encontrado na tabela automated_prices")
    
    # Verificar se há dados de hoje
    cursor.execute("""
        SELECT COUNT(*) 
        FROM automated_prices 
        WHERE last_updated::date = CURRENT_DATE
    """)
    
    today_count = cursor.fetchone()[0]
    print(f"\n📊 Total de registos atualizados hoje: {today_count}")
    
    # Verificar dados para Faro especificamente
    cursor.execute("""
        SELECT COUNT(*), MAX(last_updated)
        FROM automated_prices 
        WHERE location LIKE '%Faro%'
    """)
    
    faro_count, faro_last = cursor.fetchone()
    print(f"📍 Faro: {faro_count} registos | Última atualização: {faro_last}")
    
    # Verificar total de registos
    cursor.execute("SELECT COUNT(*) FROM automated_prices")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total geral de registos: {total}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
