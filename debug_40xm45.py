#!/usr/bin/env python3
"""
Debug script to check ALL data related to 40-XM-45 in the database
"""
import os
import psycopg2
from urllib.parse import urlparse

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    # Parse URL
    result = urlparse(database_url)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO COMPLETO: 40-XM-45")
    print("="*80 + "\n")
    
    # 1. Check rental_agreements
    print("1️⃣ RENTAL AGREEMENTS com 40-XM-45:")
    print("-" * 80)
    cur.execute("""
        SELECT id, rental_agreement_number, license_plate, vehicle_id, 
               inspection_completed, created_at
        FROM rental_agreements
        WHERE UPPER(license_plate) = '40-XM-45'
        ORDER BY created_at DESC
    """)
    ras = cur.fetchall()
    if ras:
        for ra in ras:
            print(f"  RA: {ra[1]}, Plate: {ra[2]}, Vehicle ID: {ra[3]}")
            print(f"      Inspection completed: {ra[4]}, Created: {ra[5]}")
    else:
        print("  ✅ Nenhum RA encontrado")
    
    # 2. Check vehicle_inspections
    print("\n2️⃣ INSPEÇÕES com 40-XM-45:")
    print("-" * 80)
    cur.execute("""
        SELECT inspection_number, contract_number, vehicle_plate, 
               inspection_type, status, created_at
        FROM vehicle_inspections
        WHERE UPPER(vehicle_plate) = '40-XM-45'
        ORDER BY created_at DESC
    """)
    inspections = cur.fetchall()
    if inspections:
        for insp in inspections:
            print(f"  Inspection: {insp[0]}")
            print(f"    Contract: {insp[1]}, Type: {insp[3]}, Status: {insp[4]}")
            print(f"    Created: {insp[5]}")
    else:
        print("  ✅ Nenhuma inspeção encontrada")
    
    # 3. Check vehicle_swaps
    print("\n3️⃣ TROCAS envolvendo 40-XM-45:")
    print("-" * 80)
    cur.execute("""
        SELECT id, rental_agreement_number, old_plate, new_plate, 
               swap_datetime, created_at
        FROM vehicle_swaps
        WHERE UPPER(old_plate) = '40-XM-45' OR UPPER(new_plate) = '40-XM-45'
        ORDER BY created_at DESC
    """)
    swaps = cur.fetchall()
    if swaps:
        for swap in swaps:
            print(f"  Swap ID: {swap[0]}, RA: {swap[1]}")
            print(f"    Old: {swap[2]} → New: {swap[3]}")
            print(f"    Swap time: {swap[4]}, Created: {swap[5]}")
    else:
        print("  ✅ Nenhuma troca encontrada")
    
    # 4. Check vehicles table
    print("\n4️⃣ VEÍCULO 40-XM-45 na tabela vehicles:")
    print("-" * 80)
    cur.execute("""
        SELECT id, matricula, grupo, marca, modelo, status, km_atual, nivel_combustivel
        FROM vehicles
        WHERE UPPER(matricula) = '40-XM-45'
    """)
    vehicle = cur.fetchone()
    if vehicle:
        print(f"  ID: {vehicle[0]}, Plate: {vehicle[1]}")
        print(f"  Group: {vehicle[2]}, Brand: {vehicle[3]}, Model: {vehicle[4]}")
        print(f"  Status: {vehicle[5]}, KM: {vehicle[6]}, Fuel: {vehicle[7]}")
    else:
        print("  ❌ Veículo não encontrado na tabela vehicles")
    
    # 5. Check for any inspections with contract_number containing '06761'
    print("\n5️⃣ TODAS as inspeções do RA 06761 (qualquer variação):")
    print("-" * 80)
    cur.execute("""
        SELECT inspection_number, contract_number, vehicle_plate, 
               inspection_type, status, created_at
        FROM vehicle_inspections
        WHERE contract_number LIKE '%06761%'
        ORDER BY created_at DESC
    """)
    all_06761_inspections = cur.fetchall()
    if all_06761_inspections:
        for insp in all_06761_inspections:
            print(f"  Inspection: {insp[0]}")
            print(f"    Contract: {insp[1]}, Plate: {insp[2]}, Type: {insp[3]}, Status: {insp[4]}")
            print(f"    Created: {insp[5]}")
    else:
        print("  ✅ Nenhuma inspeção encontrada para RA 06761")
    
    print("\n" + "="*80)
    print("FIM DO DIAGNÓSTICO")
    print("="*80 + "\n")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
