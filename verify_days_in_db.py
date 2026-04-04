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

# Verificar alguns registos de março 2026
cursor.execute("""
    SELECT 
        c.name,
        cb.voucher_number,
        cb.pickup_date,
        cb.dropoff_date,
        (cb.dropoff_date - cb.pickup_date) as dias_calculados,
        cb.commission_amount
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE EXTRACT(MONTH FROM cb.pickup_date) = 3
      AND EXTRACT(YEAR FROM cb.pickup_date) = 2026
    ORDER BY cb.pickup_date
    LIMIT 10
""")

print("📊 Amostra de registos de Março 2026:")
print(f"{'Comissionista':<25} {'Voucher':<10} {'Pickup':<12} {'Dropoff':<12} {'Dias':<5} {'Comissão'}")
print("=" * 90)
for row in cursor.fetchall():
    dias = row[4] if row[4] is not None else 0
    print(f"{row[0]:<25} {str(row[1] or '-'):<10} {row[2]} {row[3]} {dias:<5} €{row[5]:.2f}")

# Verificar totais
cursor.execute("""
    SELECT 
        EXTRACT(YEAR FROM pickup_date) as ano,
        COUNT(*) as total
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
    GROUP BY EXTRACT(YEAR FROM pickup_date)
    ORDER BY ano
""")

print("\n📈 Totais importados:")
for row in cursor.fetchall():
    print(f"  {int(row[0])}: {row[1]} registos")

conn.close()
