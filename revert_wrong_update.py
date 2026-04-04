#!/usr/bin/env python3
"""
Reverter a atualização incorreta de 7 dias por defeito
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

print("🔄 Revertendo atualização incorreta...")

# Reverter: colocar dropoff_date = pickup_date novamente para os registos de 2025
cursor.execute("""
    UPDATE commission_bookings
    SET dropoff_date = pickup_date
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
      AND dropoff_date = pickup_date + INTERVAL '7 days'
""")

reverted = cursor.rowcount
conn.commit()
print(f"✅ {reverted} registos revertidos")

cursor.close()
conn.close()
