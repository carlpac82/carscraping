#!/usr/bin/env python3
import pandas as pd

# Verificar dados do ficheiro de Fevereiro
file_path = 'CM-26/CM-02-2026.xlsx'
df = pd.read_excel(file_path)

print(f'=== ANÁLISE DE CM-02-2026.xlsx ===')
print(f'Total de linhas: {len(df)}')
print(f'Colunas: {list(df.columns)}')

# Encontrar brokers
broker_rows = df[df['Voucher'].notna() & (df['Voucher'].str.contains('ABBYCAR|AQUAMAR|CARJET|DISCOVERCARS|CARALLIANCE|VIP', na=False) | ~df['Voucher'].astype(str).str.isdigit().fillna(False))]
print(f'\nBrokers encontrados: {len(broker_rows)}')
for idx, row in broker_rows.iterrows():
    print(f'  - {row["Voucher"]}')

# Verificar reservas válidas (vouchers numéricos)
valid_reservations = df[df['Voucher'].notna() & df['Voucher'].astype(str).str.isdigit().fillna(False)]
print(f'\nReservas válidas (vouchers numéricos): {len(valid_reservations)}')

if len(valid_reservations) > 0:
    print('Primeiras reservas válidas:')
    for idx, row in valid_reservations.head(5).iterrows():
        print(f'  Voucher: {row["Voucher"]} - Data: {row["Data Entrega"]} - Dias: {row["Dias"]} - Preço: {row["Loyalty Card"]}')
else:
    print('Nenhuma reserva válida encontrada!')
