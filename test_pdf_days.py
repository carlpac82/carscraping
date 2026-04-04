#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse
from datetime import datetime

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

# Query igual ao PDF
query = """
    SELECT 
        cb.id, cb.voucher_number, cb.pickup_date, cb.dropoff_date,
        cb.commission_amount, c.name as commissioner_name
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE cb.commission_amount > 0
      AND EXTRACT(MONTH FROM cb.pickup_date) = 3
    ORDER BY c.name, cb.pickup_date
"""

cursor.execute(query)
rows = cursor.fetchall()

print(f"Total de registos: {len(rows)}\n")

for row in rows[:10]:
    commissioner_name = row[5] if len(row) > 5 and row[5] else "Sem Comissionista"
    
    # Processar datas como no código do PDF
    from datetime import date as date_type
    
    if row[2]:
        if isinstance(row[2], str):
            pickup_date = datetime.fromisoformat(row[2])
        elif isinstance(row[2], date_type):
            pickup_date = datetime.combine(row[2], datetime.min.time())
        else:
            pickup_date = row[2]
    else:
        pickup_date = None
    
    if row[3]:
        if isinstance(row[3], str):
            dropoff_date = datetime.fromisoformat(row[3])
        elif isinstance(row[3], date_type):
            dropoff_date = datetime.combine(row[3], datetime.min.time())
        else:
            dropoff_date = row[3]
    else:
        dropoff_date = None
    
    days = (dropoff_date - pickup_date).days if pickup_date and dropoff_date else 0
    
    print(f"Comissionista: {commissioner_name}")
    print(f"  Voucher: {row[1]}")
    print(f"  Pickup (raw): {row[2]} (type: {type(row[2])})")
    print(f"  Dropoff (raw): {row[3]} (type: {type(row[3])})")
    print(f"  Pickup (processed): {pickup_date}")
    print(f"  Dropoff (processed): {dropoff_date}")
    print(f"  Dias calculados: {days}")
    print(f"  Comissão: €{row[4]:.2f}")
    print()

conn.close()
