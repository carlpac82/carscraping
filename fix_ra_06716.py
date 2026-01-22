#!/usr/bin/env python3
"""
Script temporário para corrigir o extracted_data do RA 06716
Este script atualiza o extracted_data com os dados do check-in que foi feito
"""

import os
import json
import psycopg2
from urllib.parse import urlparse

# Conectar ao banco de dados
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL não encontrada")
    exit(1)

# Parse database URL
result = urlparse(database_url)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

conn = psycopg2.connect(
    database=database,
    user=username,
    password=password,
    host=hostname,
    port=port
)

cursor = conn.cursor()

# Buscar o RA 06716
cursor.execute("""
    SELECT rental_agreement_number, license_plate, extracted_data, inspection_id
    FROM rental_agreements
    WHERE rental_agreement_number = '06716'
""")

row = cursor.fetchone()
if not row:
    print("❌ RA 06716 não encontrado")
    exit(1)

ra_number, plate, extracted_data_json, inspection_id = row
print(f"✅ RA encontrado: {ra_number} - {plate}")
print(f"📦 Inspection ID: {inspection_id}")

# Parse extracted_data
extracted_data = json.loads(extracted_data_json) if extracted_data_json else {}
print(f"📦 extracted_data atual: {json.dumps(extracted_data, indent=2)}")

# Buscar dados da inspeção
if inspection_id:
    cursor.execute("""
        SELECT odometer_reading, fuel_level, created_at
        FROM vehicle_inspections
        WHERE id = %s
    """, (inspection_id,))
    
    inspection_row = cursor.fetchone()
    if inspection_row:
        odometer, fuel, created_at = inspection_row
        print(f"✅ Inspeção encontrada: kms={odometer}, fuel={fuel}, date={created_at}")
        
        # Atualizar extracted_data
        extracted_data['odometer'] = int(odometer)
        extracted_data['kms'] = int(odometer)
        extracted_data['fuel_level'] = str(fuel)
        extracted_data['combustivel'] = str(fuel)
        extracted_data['delivery_date'] = created_at.strftime('%d/%m/%Y')
        extracted_data['delivery_time'] = created_at.strftime('%H:%M')
        extracted_data['pickup_date'] = created_at.strftime('%d/%m/%Y')
        extracted_data['pickup_time'] = created_at.strftime('%H:%M')
        
        # Adicionar client_name se não existir
        if 'client_name' not in extracted_data and 'clientName' in extracted_data:
            extracted_data['client_name'] = extracted_data['clientName']
        
        updated_json = json.dumps(extracted_data)
        
        print(f"📦 extracted_data atualizado: {json.dumps(extracted_data, indent=2)}")
        
        # Atualizar no banco
        cursor.execute("""
            UPDATE rental_agreements
            SET extracted_data = %s
            WHERE rental_agreement_number = '06716'
        """, (updated_json,))
        
        conn.commit()
        print("✅ RA 06716 atualizado com sucesso!")
    else:
        print("❌ Inspeção não encontrada")
else:
    print("❌ RA não tem inspection_id associado")

cursor.close()
conn.close()
