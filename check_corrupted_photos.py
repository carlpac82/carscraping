#!/usr/bin/env python3
"""
Identificar fotos corruptas na base de dados
"""

import os
import psycopg2
import base64

database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')

conn = psycopg2.connect(database_url)
cursor = conn.cursor()

print("\n" + "="*80)
print("IDENTIFICANDO FOTOS CORRUPTAS")
print("="*80)

# Buscar todas as fotos
cursor.execute("""
    SELECT 
        ip.id,
        ip.inspection_id,
        ip.photo_type,
        ip.image_data,
        i.vehicle_plate,
        i.inspection_type,
        i.created_at
    FROM inspection_photos ip
    JOIN vehicle_inspections i ON ip.inspection_id = i.id
    WHERE ip.image_data IS NOT NULL
    ORDER BY ip.id
""")

total = 0
corrupted = 0
corrupted_inspections = {}

for row in cursor.fetchall():
    photo_id, inspection_id, photo_type, image_data, plate, insp_type, created_at = row
    total += 1
    
    try:
        # Tentar decodificar
        if isinstance(image_data, str):
            if image_data.startswith('\\x'):
                # É bytea hex - OK
                continue
            elif image_data.startswith('data:'):
                # É base64 com data URI
                image_data = image_data.split(',', 1)[1]
            
            # Limpar e adicionar padding
            image_data = image_data.strip().replace('\n', '').replace('\r', '').replace(' ', '')
            missing_padding = len(image_data) % 4
            if missing_padding:
                image_data += '=' * (4 - missing_padding)
            
            # Tentar decodificar
            base64.b64decode(image_data)
            
    except Exception as e:
        corrupted += 1
        
        # Agrupar por inspeção
        key = f"{plate}_{inspection_id}"
        if key not in corrupted_inspections:
            corrupted_inspections[key] = {
                'plate': plate,
                'inspection_id': inspection_id,
                'type': insp_type,
                'created_at': created_at,
                'photos': []
            }
        
        corrupted_inspections[key]['photos'].append({
            'photo_id': photo_id,
            'photo_type': photo_type,
            'error': str(e)[:50]
        })

conn.close()

print(f"\n📊 ESTATÍSTICAS:")
print(f"Total de fotos: {total:,}")
print(f"Fotos corruptas: {corrupted} ({corrupted*100/total:.2f}%)")
print(f"Inspeções afetadas: {len(corrupted_inspections)}")

print(f"\n" + "="*80)
print("INSPEÇÕES COM FOTOS CORRUPTAS")
print("="*80)

for key, data in sorted(corrupted_inspections.items(), key=lambda x: x[1]['created_at']):
    print(f"\n🚗 Matrícula: {data['plate']}")
    print(f"   ID Inspeção: {data['inspection_id']}")
    print(f"   Tipo: {data['type']}")
    print(f"   Data: {data['created_at']}")
    print(f"   Fotos corruptas ({len(data['photos'])}):")
    for photo in data['photos']:
        print(f"      - {photo['photo_type']} (ID: {photo['photo_id']}) - {photo['error']}")

print("\n" + "="*80)
print("FIM DO RELATÓRIO")
print("="*80)
