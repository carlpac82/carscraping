#!/usr/bin/env python3
import pandas as pd

# Análise profunda do ficheiro de Março
file_path = 'CM-26/CM-03-2026.xlsx'
df = pd.read_excel(file_path)

print(f'=== ANÁLISE PROFUNDA CM-03-2026.xlsx ===')
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
    
    # Se temos um broker atual e esta linha tem dados
    if current_broker and current_broker_id:
        pickup_date = row['Data Entrega']
        days = row['Dias']
        total_price = row['Loyalty Card']
        
        if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
            reserva_info = {
                'linha': idx,
                'voucher': voucher if voucher else 'SEM_VOUCHER',
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

# Verificar se há vouchers vazios com dados
print(f'\n=== VERIFICANDO VOUCHERS VAZIOS COM DADOS ===')
vazios_com_dados = 0
broker_atual = None

for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    pickup_date = row['Data Entrega']
    days = row['Dias']
    total_price = row['Loyalty Card']
    
    # Atualizar broker atual
    if voucher in broker_mapping:
        broker_atual = voucher
    elif voucher and voucher != '' and not voucher.isdigit():
        broker_atual = None
    
    # Verificar se tem voucher vazio mas com dados
    if (voucher == '' or voucher == 'nan') and pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price) and broker_atual:
        vazios_com_dados += 1
        print(f'  Linha {idx}: Voucher VAZIO | Broker: {broker_atual} | Data={pickup_date} | Dias={days} | Preço={total_price}')

print(f'\nTotal de linhas com voucher vazio mas com dados: {vazios_com_dados}')

# Verificar brokers especiais que podem ter reservas faltantes
print(f'\n=== VERIFICANDO BROKERS ESPECIAIS ===')
special_brokers = ['API', 'BROKERS - DIRECTOS']

for special in special_brokers:
    print(f'\n🔍 Verificando {special}:')
    found_line = None
    for idx, row in df.iterrows():
        voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
        if voucher == special:
            found_line = idx
            print(f'  Encontrado na linha {idx}')
            break
    
    if found_line:
        # Verificar linhas depois do broker
        count = 0
        for idx in range(found_line + 1, len(df)):
            row = df.iloc[idx]
            voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
            pickup_date = row['Data Entrega']
            days = row['Dias']
            total_price = row['Loyalty Card']
            
            # Parar quando encontrar outro broker
            if voucher and not voucher.isdigit() and voucher != '' and voucher != 'nan':
                break
            
            # Contar se tiver dados válidos
            if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
                count += 1
                print(f'    ✅ Linha {idx}: {pickup_date} - {days} dias - €{total_price}')
        
        print(f'  📊 Total de reservas encontradas: {count}')
    else:
        print(f'  ❌ Broker {special} não encontrado no ficheiro')
