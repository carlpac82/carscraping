#!/usr/bin/env python3
"""
Debug: Ver quais registos de 2026 estão a ser ignorados e porquê
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse

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

# Mapeamento de hotéis
hotel_mapping = {
    'CERRO MAR GARDEM': 'CERRO MAR GARDEM',
    'CLUBE MARIA LUISA': 'CLUBE MARIA LUISA',
    'EPIC SANA': 'EPIC SANA',
    'EXPOSE I': 'EXPOSE I',
    'FALESIA HOTEL': 'FALESIA HOTEL',
    'HOLIDAY IN (REAL BELA VISTA)': 'HOLIDAY IN (REAL BELA VISTA)',
    'INATEL': 'INATEL',
    'MASANA': 'MASANA',
    'OCEANUS': 'OCEANUS',
    'OURA ATLANTICO': 'OURA ATLANTICO',
    'OURA VIEW BEACH CLUB': 'OURA VIEW BEACH CLUB',
    'PALADIM': 'PALADIM',
    'PATEO VILLAGE': 'PATEO VILLAGE',
    'PATIO SUITE HOTEL': 'PATIO SUITE HOTEL',
    'PTO': 'PTO',
    'ROCAMAR': 'ROCAMAR',
    'SOL E MAR': 'SOL E MAR',
    'ZEBRA SAFARIS II': 'ZEBRA SAFARIS II'
}

cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}

print("🔍 Analisando ficheiros de 2026 para encontrar registos ignorados...\n")

for month in range(1, 4):
    filename = f'CM-{month:02d}-2026.xlsx'
    
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
            # Buscar ID do comissionista
            commissioner_id = None
            for hotel_name, comm_name in hotel_mapping.items():
                if hotel_name in current_hotel:
                    commissioner_id = commissioners.get(comm_name.upper())
                    break
            
            if not commissioner_id:
                print(f"  ❌ Linha {idx}: Hotel '{current_hotel}' não encontrado")
                print(f"      Data: {row.get('Data Entrega')}")
                continue
            
            # Verificar voucher duplicado
            manual_voucher = None
            if pd.notna(row.get('Voucher')):
                voucher_str = str(row['Voucher']).strip()
                if voucher_str and voucher_str != 'nan' and voucher_str.upper() != current_hotel:
                    manual_voucher = voucher_str
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM commission_bookings 
                        WHERE voucher_number = %s
                    """, (manual_voucher,))
                    
                    if cursor.fetchone()[0] > 0:
                        print(f"  ⚠️  Linha {idx}: Voucher '{manual_voucher}' duplicado")
                        print(f"      Hotel: {current_hotel}")
                        print(f"      Data: {row.get('Data Entrega')}")

conn.close()
