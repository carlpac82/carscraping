#!/usr/bin/env python3
import pandas as pd

# Verificar dados mais detalhados
files = ['CM-26/CM-01-2026.xlsx', 'CM-26/CM-02-2026.xlsx', 'CM-26/CM-03-2026.xlsx']

for file in files:
    try:
        print(f'\n=== {file} ===')
        df = pd.read_excel(file)
        
        # Encontrar brokers (nomes específicos)
        broker_rows = df[df['Voucher'].notna() & (df['Voucher'].str.contains('ABBYCAR|AQUAMAR', na=False) | ~df['Voucher'].astype(str).str.isdigit().fillna(False))]
        print('Brokers encontrados:')
        for idx, row in broker_rows.iterrows():
            print(f'  - {row["Voucher"]}')
        
        # Verificar linhas com dados válidos
        valid_rows = df[df['Voucher'].notna() & df['Voucher'].astype(str).str.isdigit().fillna(False)]
        print(f'Total de reservas válidas: {len(valid_rows)}')
        
        if len(valid_rows) > 0:
            print('Exemplo de reserva válida:')
            print(valid_rows.iloc[0].to_string())
        
    except Exception as e:
        print(f'Erro ao ler {file}: {e}')
