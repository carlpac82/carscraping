#!/usr/bin/env python3
"""
Script para corrigir o RA da inspeção para o formato correto
De: 07113 para 07113-09
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_inspection_ra():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔍 Procurando inspeção ID 835...")
    
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type
        FROM vehicle_inspections
        WHERE id = 835
    """)
    
    inspection = cur.fetchone()
    
    if not inspection:
        print("❌ Inspeção não encontrada")
        conn.close()
        return
    
    print(f"\n📋 Inspeção encontrada:")
    print(f"  ID: {inspection[0]}")
    print(f"  RA atual: {inspection[1]}")
    print(f"  Matrícula: {inspection[2]}")
    print(f"  Tipo: {inspection[3]}")
    
    print(f"\n✏️ Corrigindo para formato correto...")
    print(f"   De: {inspection[1]}")
    print(f"   Para: 07113-09")
    
    # Update the RA
    cur.execute("""
        UPDATE vehicle_inspections
        SET contract_number = '07113-09'
        WHERE id = 835
    """)
    
    conn.commit()
    
    print(f"✅ Inspeção corrigida com sucesso!")
    
    # Verify
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type
        FROM vehicle_inspections
        WHERE id = 835
    """)
    
    result = cur.fetchone()
    print(f"\n🔍 Verificação:")
    print(f"   ID: {result[0]}")
    print(f"   RA: {result[1]}")
    print(f"   Matrícula: {result[2]}")
    print(f"   Tipo: {result[3]}")
    
    conn.close()

if __name__ == "__main__":
    fix_inspection_ra()
