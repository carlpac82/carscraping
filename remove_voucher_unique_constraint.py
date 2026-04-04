#!/usr/bin/env python3
"""
Remover constraint UNIQUE de voucher_number
"""
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

print("🔍 Verificando constraints em voucher_number...")

# Verificar se existe constraint UNIQUE
cursor.execute("""
    SELECT constraint_name 
    FROM information_schema.table_constraints 
    WHERE table_name = 'commission_bookings' 
      AND constraint_type = 'UNIQUE'
      AND constraint_name LIKE '%voucher%'
""")

constraints = cursor.fetchall()
if constraints:
    for constraint in constraints:
        print(f"  Removendo constraint: {constraint[0]}")
        cursor.execute(f"ALTER TABLE commission_bookings DROP CONSTRAINT {constraint[0]}")
    conn.commit()
    print("✅ Constraints removidas")
else:
    print("✅ Nenhuma constraint UNIQUE em voucher_number")

cursor.close()
conn.close()
