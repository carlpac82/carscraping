#!/usr/bin/env python3
"""
Importar as 3 reservas que foram ignoradas
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from datetime import timedelta

def get_database_url():
    database_url = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    return database_url

def import_missing_reservations():
    print("=" * 80)
    print("IMPORTAR RESERVAS IGNORADAS - 2025")
    print("=" * 80)
    
    database_url = get_database_url()
    result = urlparse(database_url)
    
    conn = psycopg2.connect(
        database="railway",
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    cursor = conn.cursor()
    
    # Mapeamento atualizado com os hotéis que faltavam
    hotel_mapping = {
        'BELA VISTA AVENIDA': 'BELA VISTA AVENIDA',
        'INATEL PRAIA': 'INATEL PRAIA'
    }
    
    # Buscar comissionistas
    cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
    commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
    
    # Reservas ignoradas específicas
    missing_reservations = [
        {
            'file': '/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-01-2025.xlsx',
            'hotel': 'BELA VISTA AVENIDA',
            'date_str': '2025-01-12',
            'days': 26,
            'loyalty_card': 360.00
        },
        {
            'file': '/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-06-2025.xlsx',
            'hotel': 'INATEL PRAIA',
            'date_str': '2025-06-21',
            'days': 1,
            'loyalty_card': 80.00
        },
        {
            'file': '/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-07-2025.xlsx',
            'hotel': 'INATEL PRAIA',
            'date_str': '2025-07-09',
            'days': 3,
            'loyalty_card': 70.00
        }
    ]
    
    imported_count = 0
    
    for res in missing_reservations:
        print(f"\n📄 Processando: {res['hotel']}")
        
        # Verificar se o comissionista existe
        commissioner_name = hotel_mapping.get(res['hotel'])
        commissioner_id = commissioners.get(commissioner_name.upper()) if commissioner_name else None
        
        if not commissioner_id:
            print(f"  ❌ Comissionista não encontrado: {res['hotel']}")
            continue
        
        # Calcular datas
        pickup_date = pd.to_datetime(res['date_str'])
        dropoff_date = pickup_date + timedelta(days=res['days'])
        
        # Calcular comissão
        base_price = res['loyalty_card']
        net_price = base_price / 1.23
        commission_amount = net_price * 0.15
        
        # Inserir reserva
        try:
            cursor.execute("""
                INSERT INTO commission_bookings (
                    commissioner_id, voucher_number, client_name, client_email, client_phone,
                    pickup_date, pickup_time, dropoff_date, dropoff_time,
                    pickup_location, dropoff_location, vehicle_group, extras,
                    price, base_price, deposit, status, commission_rate, commission_amount,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """, (
                commissioner_id, None, 'Loyalty Card', '', '',
                pickup_date.date(), pickup_date.strftime('%H:%M'), 
                dropoff_date.date(), '00:00',
                '', '', 'LOYALTY', '[]',
                base_price, base_price, 0, 'confirmed', 15.0, commission_amount
            ))
            
            print(f"  ✅ {pickup_date.strftime('%d/%m/%Y')} - {res['days']} dias - Total: €{base_price:.2f} - Comissão: €{commission_amount:.2f}")
            imported_count += 1
            
        except Exception as e:
            print(f"  ❌ Erro ao importar: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 80)
    print(f"✅ Importação concluída!")
    print(f"  - Reservas importadas: {imported_count}")
    print("=" * 80)

if __name__ == "__main__":
    import_missing_reservations()
