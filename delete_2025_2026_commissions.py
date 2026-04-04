#!/usr/bin/env python3
"""
Apagar todos os registos de commission_bookings de 2025 e 2026
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

# Contar registos antes de apagar
cursor.execute("""
    SELECT 
        EXTRACT(YEAR FROM pickup_date) as year,
        COUNT(*)
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
    GROUP BY EXTRACT(YEAR FROM pickup_date)
    ORDER BY year
""")

print("Registos a apagar:")
for row in cursor.fetchall():
    print(f"  {int(row[0])}: {row[1]} registos")

# Apagar
cursor.execute("""
    DELETE FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
""")

deleted = cursor.rowcount
conn.commit()
print(f"\n✅ {deleted} registos apagados")

cursor.close()
conn.close()
