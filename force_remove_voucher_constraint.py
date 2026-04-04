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

# Listar TODAS as constraints da tabela
cursor.execute("""
    SELECT constraint_name, constraint_type
    FROM information_schema.table_constraints 
    WHERE table_name = 'commission_bookings'
""")

print("Constraints em commission_bookings:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Remover especificamente a constraint de voucher_number
try:
    cursor.execute("ALTER TABLE commission_bookings DROP CONSTRAINT commission_bookings_voucher_number_unique")
    conn.commit()
    print("\n✅ Constraint commission_bookings_voucher_number_unique removida")
except Exception as e:
    print(f"\n⚠️  Erro ao remover: {e}")

cursor.close()
conn.close()
