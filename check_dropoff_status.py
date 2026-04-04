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

# Verificar estado dos dropoff_dates
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN dropoff_date IS NULL THEN 1 END) as null_dropoff,
        COUNT(CASE WHEN dropoff_date = pickup_date THEN 1 END) as same_date,
        COUNT(CASE WHEN dropoff_date > pickup_date THEN 1 END) as valid_dates
    FROM commission_bookings
    WHERE EXTRACT(MONTH FROM pickup_date) = 3
      AND EXTRACT(YEAR FROM pickup_date) = 2026
""")

stats = cursor.fetchone()
print(f"Março 2026:")
print(f"  Total: {stats[0]}")
print(f"  dropoff_date NULL: {stats[1]}")
print(f"  dropoff_date = pickup_date: {stats[2]}")
print(f"  dropoff_date > pickup_date: {stats[3]}")

# Ver exemplos
cursor.execute("""
    SELECT voucher_number, pickup_date, dropoff_date
    FROM commission_bookings
    WHERE EXTRACT(MONTH FROM pickup_date) = 3
      AND EXTRACT(YEAR FROM pickup_date) = 2026
    LIMIT 10
""")

print("\nExemplos:")
for row in cursor.fetchall():
    print(f"  Voucher: {row[0]}, Pickup: {row[1]}, Dropoff: {row[2]}")

conn.close()
