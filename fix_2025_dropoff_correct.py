#!/usr/bin/env python3
"""
Corrigir dropoff_date de 2025 lendo dias dos ficheiros Excel
Procura por comissionista + pickup_date (sem usar voucher)
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

print("✅ Conectado à base de dados")

# Buscar todos os comissionistas
cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}

# Mapeamento de nomes nos ficheiros Excel para nomes na BD
name_mapping = {
    'ALBUFEIRA SOL': 'ALBUFEIRA SOL',
    'APARTAMENTOS CABRITA': 'APARTAMENTOS CABRITA',
    'AQUAMAR': 'AQUAMAR',
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

# Buscar todos os registos de 2025 que precisam de correção
cursor.execute("""
    SELECT cb.id, cb.pickup_date, c.name
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
      AND cb.dropoff_date = cb.pickup_date
    ORDER BY c.name, cb.pickup_date
""")

bookings_to_fix = cursor.fetchall()
print(f"\n📊 Total de registos a corrigir: {len(bookings_to_fix)}")

# Criar mapa: (comissionista, data) -> booking_id
bookings_map = {}
for booking_id, pickup_date, comm_name in bookings_to_fix:
    key = (comm_name, pickup_date)
    if key not in bookings_map:
        bookings_map[key] = []
    bookings_map[key].append(booking_id)

print(f"📋 Mapa criado com {len(bookings_map)} chaves únicas")

# Processar ficheiros Excel
total_updated = 0

for month in range(1, 13):
    filename = f'2025/CM-{month:02d}-2025.xlsx'
    
    if not os.path.exists(filename):
        continue
    
    print(f"\n📄 {filename}...")
    
    # Ler ficheiro - verificar se tem estrutura de comissionistas
    df = pd.read_excel(filename)
    
    # Verificar se é ficheiro de brokers (tem vouchers de brokers) ou comissionistas
    # Ficheiros de comissionistas têm estrutura: nome do hotel como linha, depois reservas
    
    current_hotel = None
    updated_count = 0
    
    for idx, row in df.iterrows():
        # Linha com nome do hotel (voucher preenchido mas sem data)
        if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
            hotel_name = str(row['Voucher']).strip().upper()
            # Verificar se é um nome de comissionista conhecido
            matched = False
            for excel_name, db_name in name_mapping.items():
                if excel_name.upper() in hotel_name:
                    current_hotel = db_name
                    matched = True
                    break
            if not matched:
                current_hotel = None
            continue
        
        # Linha com reserva
        if pd.notna(row.get('Data Entrega')) and current_hotel:
            try:
                pickup_date = pd.to_datetime(row['Data Entrega']).date()
                days = int(row['Dias']) if pd.notna(row.get('Dias')) else 1
                
                # Procurar booking correspondente
                key = (current_hotel, pickup_date)
                if key in bookings_map and bookings_map[key]:
                    booking_id = bookings_map[key].pop(0)
                    
                    # Calcular dropoff_date
                    dropoff_date = pickup_date + timedelta(days=days)
                    
                    # Atualizar
                    cursor.execute("""
                        UPDATE commission_bookings
                        SET dropoff_date = %s
                        WHERE id = %s
                    """, (dropoff_date, booking_id))
                    
                    updated_count += 1
                    
            except Exception as e:
                print(f"  ⚠️  Erro linha {idx}: {e}")
                continue
    
    conn.commit()
    print(f"  ✅ {updated_count} atualizados")
    total_updated += updated_count

print(f"\n{'='*80}")
print(f"✅ Total atualizado: {total_updated}")
print(f"{'='*80}")

# Verificar quantos ainda faltam
cursor.execute("""
    SELECT COUNT(*) 
    FROM commission_bookings 
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
      AND dropoff_date = pickup_date
""")
remaining = cursor.fetchone()[0]
print(f"\n⚠️  Ainda faltam: {remaining}")

cursor.close()
conn.close()
