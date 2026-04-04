#!/usr/bin/env python3
"""
Remover vouchers gerados automaticamente (COMM-*) e deixar NULL
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

print("🔍 Verificando vouchers automáticos...")

# Ver quantos vouchers COMM- existem
cursor.execute("""
    SELECT COUNT(*) 
    FROM commission_bookings 
    WHERE voucher_number LIKE 'COMM-%'
""")
total = cursor.fetchone()[0]
print(f"Total de vouchers COMM-*: {total}")

# Remover vouchers automáticos
cursor.execute("""
    UPDATE commission_bookings
    SET voucher_number = NULL
    WHERE voucher_number LIKE 'COMM-%'
""")

removed = cursor.rowcount
conn.commit()
print(f"✅ {removed} vouchers automáticos removidos (agora NULL)")

cursor.close()
conn.close()
