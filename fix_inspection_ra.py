#!/usr/bin/env python3
"""
Script para corrigir o RA da inspeção recém-guardada
De: 06836-09 para 07113
Matrícula: BB-89-RA
"""

import psycopg2
import os
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_inspection_ra():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Find the most recent inspection with RA 06836-09 and plate BB-89-RA
    print("🔍 Procurando inspeção recente com RA 06836-09 e matrícula BB-89-RA...")
    
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type, created_at
        FROM vehicle_inspections
        WHERE contract_number LIKE '06836%'
        AND UPPER(vehicle_plate) = 'BB-89-RA'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    inspections = cur.fetchall()
    
    if not inspections:
        print("❌ Nenhuma inspeção encontrada")
        conn.close()
        return
    
    print(f"\n📋 Encontradas {len(inspections)} inspeções:")
    for insp in inspections:
        print(f"  ID: {insp[0]}, RA: {insp[1]}, Matrícula: {insp[2]}, Tipo: {insp[3]}, Data: {insp[4]}")
    
    # Get the most recent one (first in list)
    inspection_id = inspections[0][0]
    old_ra = inspections[0][1]
    
    print(f"\n✏️ Corrigindo inspeção ID {inspection_id}...")
    print(f"   De: {old_ra}")
    print(f"   Para: 07113")
    
    # Update the RA
    cur.execute("""
        UPDATE vehicle_inspections
        SET contract_number = '07113'
        WHERE id = %s
    """, (inspection_id,))
    
    conn.commit()
    
    print(f"✅ Inspeção corrigida com sucesso!")
    
    # Verify
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type
        FROM vehicle_inspections
        WHERE id = %s
    """, (inspection_id,))
    
    result = cur.fetchone()
    print(f"\n🔍 Verificação:")
    print(f"   ID: {result[0]}")
    print(f"   RA: {result[1]}")
    print(f"   Matrícula: {result[2]}")
    print(f"   Tipo: {result[3]}")
    
    conn.close()

if __name__ == "__main__":
    fix_inspection_ra()
