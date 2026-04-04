#!/usr/bin/env python3
"""
Debug: Ver quais registos de 2025 estão a ser ignorados e porquê
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

database_url = os.getenv('DATABASE_URL')
if not database_url:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                database_url = line.split('=', 1)[1].strip()
                break

result = urlparse(database_url)
conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cursor = conn.cursor()

# Buscar comissionistas
cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}

print("🔍 Analisando ficheiros de 2025 para encontrar registos ignorados...\n")

for month in [4, 10]:  # Meses que tiveram registos ignorados
    filename = f'2025/CM-{month:02d}-2025.xlsx'
    
    if not os.path.exists(filename):
        continue
    
    print(f"\n📄 {filename}")
    df = pd.read_excel(filename)
    
    current_hotel = None
    
    for idx, row in df.iterrows():
        # Identificar nome do hotel
        if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
            current_hotel = str(row['Voucher']).strip().upper()
            continue
        
        # Processar reserva
        if pd.notna(row.get('Data Entrega')) and current_hotel:
            commissioner_id = commissioners.get(current_hotel)
            
            if not commissioner_id:
                print(f"  ❌ Linha {idx}: Hotel '{current_hotel}' não encontrado na BD")
                continue
            
            try:
                pickup_date = pd.to_datetime(row['Data Entrega'])
                days = int(row['Dias']) if pd.notna(row.get('Dias')) else 1
                
                # Verificar voucher
                manual_voucher = None
                if pd.notna(row.get('Voucher')):
                    voucher_str = str(row['Voucher']).strip()
                    if voucher_str and voucher_str != 'nan' and voucher_str.upper() != current_hotel:
                        manual_voucher = voucher_str
                
                # Verificar se já existe na BD
                if manual_voucher:
                    cursor.execute("""
                        SELECT COUNT(*) FROM commission_bookings 
                        WHERE voucher_number = %s
                    """, (manual_voucher,))
                    
                    if cursor.fetchone()[0] > 0:
                        print(f"  ⚠️  Linha {idx}: Voucher '{manual_voucher}' duplicado - IGNORADO")
                        print(f"      Hotel: {current_hotel}")
                        print(f"      Data: {pickup_date.strftime('%d/%m/%Y')}")
                        print(f"      Dias: {days}")
                
            except Exception as e:
                print(f"  ❌ Linha {idx}: Erro - {e}")
                print(f"      Dados: {row.to_dict()}")

conn.close()
