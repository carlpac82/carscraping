#!/usr/bin/env python3
import pandas as pd

# Análise profunda do ficheiro de Fevereiro
file_path = 'CM-26/CM-02-2026.xlsx'
df = pd.read_excel(file_path)

print(f'=== ANÁLISE PROFUNDA CM-02-2026.xlsx ===')
print(f'Total de linhas: {len(df)}')
print(f'Colunas: {list(df.columns)}')

# Mapeamento de brokers corretos
broker_mapping = {
    'ABBYCAR-POA': 245,
    'ABBYCAR-PREPAID': 236,
    'AP': 157,
    'API-WEB': 200,
    'API': 200,
    'BROKERS - DIRECTOS': 252,
    'CARALLIANCE-POA': 253,
    'CARALLIANCE-PREPAID': 254,
    'CARJET-PREPAID': 237,
    'CARJET': 237,
    'DISCOVERCARS-PREPAID': 246,
    'DISCOVERCARS-POA': 235,
    'RENTALCARS': 191,
    'VIP CARS-POA': 232,
    'VIP CARS': 232
}

print(f'\n=== ANÁLISE POR BROKER ===')

# Analisar linha a linha
current_broker = None
current_broker_id = None
reservas_by_broker = {}

for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    
    # Verificar se é um broker válido
    if voucher in broker_mapping:
        current_broker = voucher
        current_broker_id = broker_mapping[voucher]
        print(f'\n🏢 Broker {current_broker} encontrado na linha {idx}')
        if current_broker not in reservas_by_broker:
            reservas_by_broker[current_broker] = []
        continue
    
    # Se temos um broker atual e esta linha tem voucher numérico
    if current_broker and current_broker_id and voucher.isdigit():
        pickup_date = row['Data Entrega']
        days = row['Dias']
        total_price = row['Loyalty Card']
        
        if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
            reserva_info = {
                'linha': idx,
                'voucher': voucher,
                'data': pickup_date,
                'dias': days,
                'preco': total_price
            }
            reservas_by_broker[current_broker].append(reserva_info)
            print(f'  ✅ Reserva {voucher} na linha {idx}: {pickup_date} - {days} dias - €{total_price}')

print(f'\n=== RESUMO POR BROKER ===')
for broker, reservas in reservas_by_broker.items():
    print(f'\n🏢 {broker}: {len(reservas)} reservas')
    for res in reservas:
        print(f'  Linha {res["linha"]}: {res["voucher"]} - {res["data"]} - {res["dias"]} dias - €{res["preco"]}')

# Verificar todas as linhas com dados
print(f'\n=== TODAS AS LINHAS COM DADOS ===')
for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    pickup_date = row['Data Entrega']
    days = row['Dias']
    total_price = row['Loyalty Card']
    
    if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
        print(f'Linha {idx}: Voucher="{voucher}" | Data={pickup_date} | Dias={days} | Preço={total_price}')
