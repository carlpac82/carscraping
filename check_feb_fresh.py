#!/usr/bin/env python3
import pandas as pd
import os

# Verificar ficheiro
file_path = 'CM-26/CM-02-2026.xlsx'

if os.path.exists(file_path):
    file_size = os.path.getsize(file_path)
    file_mtime = os.path.getmtime(file_path)
    print(f'=== CM-02-2026.xlsx ===')
    print(f'Tamanho: {file_size} bytes')
    print(f'Modificado: {file_mtime}')
    
    # Ler ficheiro
    df = pd.read_excel(file_path)
    
    print(f'Total de linhas: {len(df)}')
    print(f'Colunas: {list(df.columns)}')
    
    # Mostrar primeiras linhas
    print('\nPrimeiras 15 linhas:')
    for idx, row in df.head(15).iterrows():
        print(f'  {idx}: Voucher={row["Voucher"]} | Data={row["Data Entrega"]} | Dias={row["Dias"]} | Preço={row["Loyalty Card"]}')
    
    # Encontrar brokers
    broker_mask = df['Voucher'].notna() & (~df['Voucher'].astype(str).str.isdigit().fillna(False))
    broker_rows = df[broker_mask]
    print(f'\nBrokers encontrados: {len(broker_rows)}')
    for idx, row in broker_rows.iterrows():
        print(f'  Linha {idx}: {row["Voucher"]}')
        
    # Verificar reservas válidas
    valid_reservations = df[df['Voucher'].notna() & df['Voucher'].astype(str).str.isdigit().fillna(False)]
    print(f'\nReservas válidas: {len(valid_reservations)}')
    for idx, row in valid_reservations.iterrows():
        print(f'  Voucher: {row["Voucher"]} - Data: {row["Data Entrega"]} - Dias: {row["Dias"]} - Preço: {row["Loyalty Card"]}')
else:
    print('Ficheiro não encontrado!')
