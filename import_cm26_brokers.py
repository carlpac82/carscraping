#!/usr/bin/env python3
import pandas as pd
import sqlite3
from datetime import datetime
import sys

def import_cm26_brokers():
    # Conectar à base de dados
    conn = sqlite3.connect('data.db')
    
    # Verificar brokers na tabela commissioners
    df_commissioners = pd.read_sql_query('SELECT id, name FROM commissioners WHERE is_broker = 1 ORDER BY name', conn)
    print(f'Brokers encontrados na base de dados: {len(df_commissioners)}')
    for name in df_commissioners['name']:
        print(f'  - {name}')
    
    # Mapeamento de brokers (Excel -> DB)
    broker_mapping = {
        'ABBYCAR-POA': 'ABBYCAR-POA',
        'ABBYCAR-PREPAID': 'ABBYCAR-PREPAID',
        'AQUAMAR': 'AQUAMAR',
        'CARJET-PREPAID': 'CARJET-PREPAID',
        'DISCOVERCARS-PREPAID': 'DISCOVERCARS-PREPAID',
        'CARALLIANCE-POA': 'CARALLIANCE-POA',
        'CARALLIANCE-PREPAID': 'CARALLIANCE-PREPAID',
        'VIP CARS-POA': 'VIP CARS-POA'
    }
    
    # Ficheiros a processar
    files = ['CM-26/CM-01-2026.xlsx', 'CM-26/CM-02-2026.xlsx', 'CM-26/CM-03-2026.xlsx']
    
    total_imported = 0
    
    for file in files:
        print(f'\n=== Processando {file} ===')
        
        try:
            # Ler Excel
            df = pd.read_excel(file)
            
            # Encontrar broker atual
            current_broker = None
            broker_id = None
            
            for idx, row in df.iterrows():
                voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
                
                # Verificar se é um broker
                if voucher in broker_mapping:
                    current_broker = broker_mapping[voucher]
                    # Obter broker_id
                    broker_row = df_commissioners[df_commissioners['name'] == current_broker]
                    if not broker_row.empty:
                        broker_id = broker_row.iloc[0]['id']
                    print(f'Broker encontrado: {current_broker} (ID: {broker_id})')
                    continue
                
                # Se temos um broker atual e esta linha tem dados válidos
                if current_broker and broker_id and voucher.isdigit():
                    # Extrair dados da reserva
                    pickup_date = row['Data Entrega']
                    days = row['Dias']
                    total_price = row['Loyalty Card']
                    
                    if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
                        # Inserir na tabela broker_bookings
                        insert_data = {
                            'broker_name': current_broker,
                            'voucher_number': voucher,
                            'client_name': 'N/A',  # Não disponível nos dados
                            'pickup_date': pickup_date,
                            'dropoff_date': pickup_date,  # Mesma data, não disponível dropoff
                            'vehicle_group': 'N/A',  # Não disponível
                            'days': int(days),
                            'total_price': float(total_price),
                            'status': 'confirmed'
                        }
                        
                        try:
                            # Verificar se já existe
                            existing = pd.read_sql_query(f'''
                                SELECT id FROM broker_bookings 
                                WHERE voucher_number = '{voucher}' AND broker_name = '{current_broker}'
                            ''', conn)
                            
                            if existing.empty:
                                # Inserir novo registro
                                cursor = conn.cursor()
                                cursor.execute('''
                                    INSERT INTO broker_bookings 
                                    (broker_name, voucher_number, client_name, pickup_date, dropoff_date, 
                                     vehicle_group, days, total_price, status, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    insert_data['broker_name'],
                                    insert_data['voucher_number'],
                                    insert_data['client_name'],
                                    insert_data['pickup_date'],
                                    insert_data['dropoff_date'],
                                    insert_data['vehicle_group'],
                                    insert_data['days'],
                                    insert_data['total_price'],
                                    insert_data['status'],
                                    datetime.now()
                                ))
                                conn.commit()
                                print(f'  ✓ Importado: {voucher} - {current_broker} - {pickup_date} - {days} dias - €{total_price}')
                                total_imported += 1
                            else:
                                print(f'  ⚠ Já existe: {voucher} - {current_broker}')
                                
                        except Exception as e:
                            print(f'  ✗ Erro ao inserir {voucher}: {e}')
                            
        except Exception as e:
            print(f'Erro ao processar {file}: {e}')
    
    print(f'\n=== Resumo ===')
    print(f'Total de registros importados: {total_imported}')
    
    conn.close()

if __name__ == '__main__':
    import_cm26_brokers()
