#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    database_url = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    return database_url

database_url = get_database_url()
result = urlparse(database_url)

conn = psycopg2.connect(
    database="railway",
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cursor = conn.cursor()

# Verificar dados por mês
cursor.execute('''
    SELECT 
        EXTRACT(MONTH FROM pickup_date) as mes,
        EXTRACT(YEAR FROM pickup_date) as ano,
        broker_name,
        COUNT(*) as total,
        SUM(total_price) as valor_total
    FROM broker_bookings 
    GROUP BY EXTRACT(MONTH FROM pickup_date), EXTRACT(YEAR FROM pickup_date), broker_name
    ORDER BY ano, mes, total DESC
''')

results = cursor.fetchall()
print('Distribuição por mês e broker:')
for result in results:
    mes, ano, broker, total, valor = result
    print(f'  {int(mes):02d}/{int(ano)} - {broker}: {total} reservas, €{valor:.2f}')

# Verificar se há dados de Fevereiro
cursor.execute('''
    SELECT COUNT(*) FROM broker_bookings 
    WHERE EXTRACT(MONTH FROM pickup_date) = 2 AND EXTRACT(YEAR FROM pickup_date) = 2026
''')
count_feb = cursor.fetchone()[0]
print(f'\nTotal de reservas em Fevereiro 2026: {count_feb}')

conn.close()
