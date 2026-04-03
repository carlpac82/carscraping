#!/usr/bin/env python3
import pandas as pd
import os
import psycopg2
from urllib.parse import urlparse

# Verificar ficheiro de Janeiro
file_path = 'CM-26/CM-01-2026.xlsx'
df = pd.read_excel(file_path)

print(f'=== ANÁLISE API-WEB EM JANEIRO 2026 ===')

# Encontrar API-WEB
api_web_line = None
for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    if voucher == 'API-WEB':
        api_web_line = idx
        print(f'API-WEB encontrado na linha {idx}')
        break

if api_web_line:
    print(f'\n=== RESERVAS API-WEB NO EXCEL ===')
    count = 0
    total_excel = 0
    reservas_excel = []
    
    for idx in range(api_web_line + 1, len(df)):
        row = df.iloc[idx]
        voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
        pickup_date = row['Data Entrega']
        days = row['Dias']
        total_price = row['Loyalty Card']
        
        # Parar quando encontrar outro broker
        if voucher and not voucher.isdigit() and voucher != '' and voucher != 'nan':
            print(f'\n🛑 Parando - Outro broker encontrado: {voucher} na linha {idx}')
            break
        
        if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
            count += 1
            total_excel += float(total_price)
            reservas_excel.append({
                'linha': idx,
                'voucher': voucher if voucher else 'SEM_VOUCHER',
                'preco': float(total_price)
            })
            print(f'  {count}. Linha {idx}: {voucher} - €{total_price}')
    
    print(f'\n📊 Total no Excel: {count} reservas, €{total_excel:.2f}')
    
    # Verificar se 4198.41 está no Excel
    print(f'\n🔍 Procurando valor €4198.41 no Excel:')
    found_4198 = False
    for res in reservas_excel:
        if abs(res['preco'] - 4198.41) < 0.01:
            print(f'  ✅ ENCONTRADO na linha {res["linha"]}: €{res["preco"]}')
            found_4198 = True
    
    if not found_4198:
        print(f'  ❌ Valor €4198.41 NÃO encontrado no Excel!')

# Verificar base de dados
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

print(f'\n=== RESERVAS API-WEB NA BASE DE DADOS (JANEIRO 2026) ===')
cursor.execute('''
    SELECT voucher_number, total_price, pickup_date
    FROM broker_bookings 
    WHERE broker_name = 'API-WEB' 
    AND EXTRACT(MONTH FROM pickup_date) = 1 
    AND EXTRACT(YEAR FROM pickup_date) = 2026
    ORDER BY total_price DESC
''')

rows = cursor.fetchall()
total_db = 0
print(f'Total de registros: {len(rows)}')

for i, row in enumerate(rows, 1):
    voucher, price, date = row
    total_db += float(price)
    print(f'  {i}. {voucher} - €{price:.2f} - {date}')

print(f'\n📊 Total na DB: {len(rows)} reservas, €{total_db:.2f}')

# Verificar se 4198.41 está na DB
print(f'\n🔍 Procurando valor €4198.41 na DB:')
found_4198_db = False
for row in rows:
    if abs(float(row[1]) - 4198.41) < 0.01:
        print(f'  ✅ ENCONTRADO: {row[0]} - €{row[1]:.2f}')
        found_4198_db = True

if not found_4198_db:
    print(f'  ❌ Valor €4198.41 NÃO encontrado na DB!')

conn.close()
