#!/usr/bin/env python3
"""
Atualizar AS-02-JQ:
- Alterar inspector_name para "Lina Prudente"
- Alterar created_at para "2026-05-06 11:47:00"
- Copiar fotos e croqui do RA: 07340
"""

import os
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
conn.autocommit = False

cursor = conn.cursor()

# 1. Buscar VI-20260507-104756-609-256 (contrato 07490-09)
print("📋 Buscando VI-20260507-104756-609-256...")
cursor.execute("""
    SELECT id, inspector_name, created_at
    FROM vehicle_inspections
    WHERE inspection_number = 'VI-20260507-104756-609-256'
""")

as_row = cursor.fetchone()
if not as_row:
    print("❌ AS-02-JQ não encontrado")
    exit(1)

as_id, old_inspector, old_date = as_row
print(f"✅ AS-02-JQ encontrado (ID: {as_id})")
print(f"   Inspector atual: {old_inspector}")
print(f"   Data atual: {old_date}")

# 2. Buscar RA: 07340
print("\n📋 Buscando RA: 07340...")
cursor.execute("""
    SELECT id
    FROM vehicle_inspections
    WHERE contract_number = '07340'
""")

ra_row = cursor.fetchone()
if not ra_row:
    print("❌ RA: 07340 não encontrado")
    exit(1)

ra_id = ra_row[0]
print(f"✅ RA: 07340 encontrado (ID: {ra_id})")

# 3. Atualizar AS-02-JQ
print("\n🔄 Atualizando AS-02-JQ...")
cursor.execute("""
    UPDATE vehicle_inspections
    SET inspector_name = %s,
        created_at = %s
    WHERE id = %s
""", ('Lina Prudente', '2026-05-06 11:47:00', as_id))

print("✅ Inspector alterado: Lina Prudente")
print("✅ Data alterada: 06/05/2026 11:47")

# 4. Contar fotos do RA: 07340
cursor.execute("""
    SELECT COUNT(*)
    FROM inspection_photos
    WHERE inspection_id = %s
""", (ra_id,))

count = cursor.fetchone()[0]
print(f"\n📸 RA: 07340 tem {count} fotos")

# 5. Apagar fotos antigas do AS-02-JQ
cursor.execute("""
    DELETE FROM inspection_photos
    WHERE inspection_id = %s
""", (as_id,))

print("🗑️  Fotos antigas do AS-02-JQ apagadas")

# 6. Copiar fotos do RA: 07340 para AS-02-JQ
cursor.execute("""
    INSERT INTO inspection_photos 
    (inspection_id, photo_type, photo_order, image_data, image_filename, 
     image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type, 
     ai_confidence, ai_result)
    SELECT %s, photo_type, photo_order, image_data, image_filename,
           image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type,
           ai_confidence, ai_result
    FROM inspection_photos
    WHERE inspection_id = %s
""", (as_id, ra_id))

print(f"✅ {count} fotos copiadas do RA: 07340 para AS-02-JQ")

# 7. Commit
conn.commit()
print("\n✅ CONCLUÍDO! AS-02-JQ atualizado com sucesso!")

cursor.close()
conn.close()
