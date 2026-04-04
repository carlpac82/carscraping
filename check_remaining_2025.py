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

# Ver quais comissionistas ainda têm registos por corrigir
cursor.execute("""
    SELECT c.name, COUNT(*), MIN(cb.pickup_date), MAX(cb.pickup_date)
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
      AND cb.dropoff_date = cb.pickup_date
    GROUP BY c.name
    ORDER BY COUNT(*) DESC
""")

print("Comissionistas com registos ainda por corrigir:")
print(f"{'Comissionista':<30} {'Qtd':<5} {'Primeira':<12} {'Última'}")
print("=" * 70)
for row in cursor.fetchall():
    print(f"{row[0]:<30} {row[1]:<5} {row[2]} {row[3]}")

# Ver alguns exemplos
print("\n\nExemplos de registos não corrigidos:")
cursor.execute("""
    SELECT cb.id, c.name, cb.pickup_date, cb.voucher_number
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
      AND cb.dropoff_date = cb.pickup_date
    ORDER BY c.name, cb.pickup_date
    LIMIT 20
""")

for row in cursor.fetchall():
    print(f"ID: {row[0]}, {row[1]}, {row[2]}, Voucher: {row[3]}")

conn.close()
