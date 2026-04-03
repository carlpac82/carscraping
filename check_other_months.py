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

print("=== VERIFICAÇÃO DE TODOS OS MESES CM-26 ===")

# Verificar dados por mês
cursor.execute('''
    SELECT 
        EXTRACT(MONTH FROM pickup_date) as mes,
        EXTRACT(YEAR FROM pickup_date) as ano,
        broker_name,
        COUNT(*) as total,
        SUM(total_price) as valor_total
    FROM broker_bookings 
    WHERE EXTRACT(YEAR FROM pickup_date) = 2026
    GROUP BY EXTRACT(MONTH FROM pickup_date), EXTRACT(YEAR FROM pickup_date), broker_name
    ORDER BY ano, mes, total DESC
''')

results = cursor.fetchall()
print('\n📊 Distribuição por mês e broker:')

current_month = None
for result in results:
    mes, ano, broker, total, valor = result
    if current_month != mes:
        print(f'\n=== {int(mes):02d}/{int(ano)} ===')
        current_month = mes
    print(f'  🏢 {broker}: {total} reservas, €{valor:.2f}')

# Totais por mês
cursor.execute('''
    SELECT 
        EXTRACT(MONTH FROM pickup_date) as mes,
        EXTRACT(YEAR FROM pickup_date) as ano,
        COUNT(*) as total,
        SUM(total_price) as valor_total
    FROM broker_bookings 
    WHERE EXTRACT(YEAR FROM pickup_date) = 2026
    GROUP BY EXTRACT(MONTH FROM pickup_date), EXTRACT(YEAR FROM pickup_date)
    ORDER BY ano, mes
''')

month_totals = cursor.fetchall()
print(f'\n📈 TOTAIS POR MÊS:')
total_geral = 0
valor_geral = 0

for mes, ano, total, valor in month_totals:
    print(f'  {int(mes):02d}/{int(ano)}: {total} reservas, €{valor:.2f}')
    total_geral += total
    valor_geral += valor

print(f'\n🎯 TOTAL GERAL CM-26: {total_geral} reservas, €{valor_geral:.2f}')

# Verificar se há reservas sem voucher numérico (possível erro)
cursor.execute('''
    SELECT 
        EXTRACT(MONTH FROM pickup_date) as mes,
        broker_name,
        COUNT(*) as total
    FROM broker_bookings 
    WHERE EXTRACT(YEAR FROM pickup_date) = 2026 
    AND voucher_number NOT SIMILAR TO '%[0-9]%'
    GROUP BY EXTRACT(MONTH FROM pickup_date), broker_name
    ORDER BY mes, total DESC
''')

vouchers_especiais = cursor.fetchall()
if vouchers_especiais:
    print(f'\n⚠️  POSSÍVEIS PROBLEMAS - Vouchers não numéricos:')
    for mes, broker, total in vouchers_especiais:
        print(f'  {int(mes):02d}/2026 - {broker}: {total} reservas com voucher especial')

conn.close()
