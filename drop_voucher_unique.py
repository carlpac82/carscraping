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

# Listar constraints
cursor.execute("""
    SELECT conname 
    FROM pg_constraint 
    WHERE conrelid = 'commission_bookings'::regclass
      AND contype = 'u'
""")

constraints = cursor.fetchall()
print("Constraints UNIQUE encontradas:")
for c in constraints:
    print(f"  - {c[0]}")
    try:
        cursor.execute(f"ALTER TABLE commission_bookings DROP CONSTRAINT {c[0]}")
        print(f"    ✅ Removida")
    except Exception as e:
        print(f"    ❌ Erro: {e}")

conn.commit()
conn.close()
