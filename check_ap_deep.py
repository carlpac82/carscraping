#!/usr/bin/env python3
import pandas as pd

# Análise profunda do broker AP no ficheiro de Fevereiro
file_path = 'CM-26/CM-02-2026.xlsx'
df = pd.read_excel(file_path)

print(f'=== ANÁLISE PROFUNDA DO BROKER AP ===')

# Encontrar onde está o broker AP
ap_line = None
for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    if voucher == 'AP':
        ap_line = idx
        print(f'Broker AP encontrado na linha {ap_line}')
        break

if ap_line is None:
    print('Broker AP não encontrado!')
    exit()

# Analisar linhas depois do AP
print(f'\n=== LINHAS DEPOIS DO AP (a partir da linha {ap_line + 1}) ===')

reservas_ap = []
for idx in range(ap_line + 1, len(df)):
    row = df.iloc[idx]
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    pickup_date = row['Data Entrega']
    days = row['Dias']
    total_price = row['Loyalty Card']
    
    # Parar quando encontrar outro broker
    if voucher and not voucher.isdigit() and voucher != '':
        print(f'\n🛑 Parando - Outro broker encontrado: {voucher} na linha {idx}')
        break
    
    # Verificar se tem dados válidos
    if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
        reserva_info = {
            'linha': idx,
            'voucher': voucher if voucher else 'SEM_VOUCHER',
            'data': pickup_date,
            'dias': days,
            'preco': total_price
        }
        reservas_ap.append(reserva_info)
        print(f'  ✅ Linha {idx}: Voucher="{voucher}" | Data={pickup_date} | Dias={days} | Preço={total_price}')

print(f'\n=== RESUMO DAS RESERVAS DO AP ===')
print(f'Total de reservas encontradas: {len(reservas_ap)}')

for i, res in enumerate(reservas_ap):
    print(f'{i+1}. Linha {res["linha"]}: {res["voucher"]} - {res["data"]} - {res["dias"]} dias - €{res["preco"]}')

# Verificar também se há vouchers vazios com dados
print(f'\n=== VERIFICANDO VOUCHERS VAZIOS COM DADOS ===')
vazios_com_dados = 0
for idx, row in df.iterrows():
    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
    pickup_date = row['Data Entrega']
    days = row['Dias']
    total_price = row['Loyalty Card']
    
    if (voucher == '' or voucher == 'nan') and pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
        vazios_com_dados += 1
        print(f'  Linha {idx}: Voucher VAZIO | Data={pickup_date} | Dias={days} | Preço={total_price}')

print(f'\nTotal de linhas com voucher vazio mas com dados: {vazios_com_dados}')
