#!/usr/bin/env python3
"""
Script para verificar as colunas da tabela vehicle_inspections
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get column names
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'vehicle_inspections'
    ORDER BY ordinal_position
""")

columns = cur.fetchall()

print("📋 Colunas da tabela vehicle_inspections:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

conn.close()
