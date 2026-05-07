#!/usr/bin/env python3
"""
Atualizar AS-02-JQ e copiar fotos do RA: 07340
"""
import sys
import os
sys.path.insert(0, '/Users/filipepacheco/CascadeProjects/carscraping')

from database import _db_connect

print("🔍 Conectando à base de dados...")
conn = _db_connect()
cursor = conn.cursor()

# Detectar PostgreSQL ou SQLite
is_postgres = hasattr(conn, '_conn')
p = '%s' if is_postgres else '?'
print(f"📊 BD: {'PostgreSQL' if is_postgres else 'SQLite'}")

# 1. Buscar AS-02-JQ
print("\n📋 Buscando AS-02-JQ...")
cursor.execute(f"SELECT id, inspector_name, created_at FROM vehicle_inspections WHERE inspection_number = {p}", ('AS-02-JQ',))
as_row = cursor.fetchone()

if not as_row:
    print("❌ AS-02-JQ não encontrado!")
    sys.exit(1)

as_id = as_row[0]
print(f"✅ ID: {as_id}, Inspector: {as_row[1]}, Data: {as_row[2]}")

# 2. Buscar RA: 07340
print("\n📋 Buscando RA: 07340...")
cursor.execute(f"SELECT id FROM vehicle_inspections WHERE contract_number = {p}", ('07340',))
ra_row = cursor.fetchone()

if not ra_row:
    print("❌ RA: 07340 não encontrado!")
    sys.exit(1)

ra_id = ra_row[0]
print(f"✅ RA ID: {ra_id}")

# 3. Atualizar AS-02-JQ
print("\n🔄 Atualizando AS-02-JQ...")
cursor.execute(f"UPDATE vehicle_inspections SET inspector_name = {p}, created_at = {p} WHERE id = {p}", 
               ('Lina Prudente', '2026-05-06 11:47:00', as_id))
print("✅ Inspector → Lina Prudente")
print("✅ Data → 06/05/2026 11:47")

# 4. Contar fotos
cursor.execute(f"SELECT COUNT(*) FROM inspection_photos WHERE inspection_id = {p}", (ra_id,))
count = cursor.fetchone()[0]
print(f"\n📸 RA: 07340 tem {count} fotos")

# 5. Apagar fotos antigas
cursor.execute(f"DELETE FROM inspection_photos WHERE inspection_id = {p}", (as_id,))
print("🗑️  Fotos antigas apagadas")

# 6. Copiar fotos
cursor.execute(f"""
INSERT INTO inspection_photos 
(inspection_id, photo_type, photo_order, image_data, image_filename, image_size, image_format, 
 ai_analyzed, ai_has_damage, ai_damage_type, ai_confidence, ai_result)
SELECT {p}, photo_type, photo_order, image_data, image_filename, image_size, image_format,
       ai_analyzed, ai_has_damage, ai_damage_type, ai_confidence, ai_result
FROM inspection_photos WHERE inspection_id = {p}
""", (as_id, ra_id))
print(f"✅ {count} fotos copiadas")

# 7. Commit
conn.commit()
print("\n✅ CONCLUÍDO!")
conn.close()
