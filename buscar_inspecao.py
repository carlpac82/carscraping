#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

database_url = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
result = urlparse(database_url)

conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)

cursor = conn.cursor()

# Procurar por contrato 07490
print("🔍 Procurando contrato 07490...")
cursor.execute("""
    SELECT inspection_number, contract_number, inspector_name, created_at
    FROM vehicle_inspections
    WHERE contract_number = '07490'
""")

rows = cursor.fetchall()
if rows:
    print(f"✅ Encontrada inspeção:")
    for row in rows:
        print(f"  Número: {row[0]}")
        print(f"  Contrato: {row[1]}")
        print(f"  Inspector: {row[2]}")
        print(f"  Data: {row[3]}")
else:
    print("❌ Nenhuma inspeção encontrada")
    
    # Procurar inspeções de hoje
    print("\n🔍 Procurando inspeções de hoje...")
    cursor.execute("""
        SELECT inspection_number, contract_number, inspector_name, created_at
        FROM vehicle_inspections
        WHERE DATE(created_at) = '2026-05-07'
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    print(f"Encontradas {len(rows)} inspeções:")
    for row in rows:
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()
