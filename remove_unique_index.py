#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
if not database_url:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                database_url = line.split('=', 1)[1].strip()
                break

result = urlparse(database_url)
conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cursor = conn.cursor()

# Verificar índices UNIQUE
cursor.execute("""
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename = 'commission_bookings'
      AND indexdef LIKE '%UNIQUE%'
""")

indexes = cursor.fetchall()
print("Índices UNIQUE encontrados:")
for idx_name, idx_def in indexes:
    print(f"\n{idx_name}:")
    print(f"  {idx_def}")
    
    if 'voucher' in idx_name.lower():
        try:
            cursor.execute(f"DROP INDEX {idx_name}")
            conn.commit()
            print(f"  ✅ Removido")
        except Exception as e:
            print(f"  ❌ Erro: {e}")

# Verificar constraints
cursor.execute("""
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'commission_bookings'::regclass
""")

print("\n\nTodas as constraints:")
for name, def_text in cursor.fetchall():
    print(f"\n{name}:")
    print(f"  {def_text}")
    
    if 'voucher' in name.lower() and 'UNIQUE' in def_text:
        try:
            cursor.execute(f"ALTER TABLE commission_bookings DROP CONSTRAINT {name}")
            conn.commit()
            print(f"  ✅ Removida")
        except Exception as e:
            print(f"  ❌ Erro: {e}")

conn.close()
