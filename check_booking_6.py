import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Buscar dados da reserva 6
cur.execute("""
    SELECT 
        cb.id, cb.commissioner_id, cb.voucher_number, cb.client_name, 
        cb.client_email, cb.client_phone, cb.hotel, cb.room_number,
        cb.pickup_date, cb.pickup_time, cb.dropoff_date, cb.dropoff_time,
        cb.pickup_location, cb.dropoff_location, cb.vehicle_group, cb.extras,
        cb.flight_number, cb.language, cb.observations, cb.deposit,
        cb.price, cb.status, cb.created_at, cb.updated_at,
        c.name as commissioner_name
    FROM commission_bookings cb
    LEFT JOIN commissioners c ON cb.commissioner_id = c.id
    WHERE cb.id = 6
""")

row = cur.fetchone()

if row:
    print("=" * 80)
    print("DADOS DA RESERVA 6:")
    print("=" * 80)
    print(f"ID: {row[0]}")
    print(f"Commissioner: {row[24]}")
    print(f"Voucher: {row[2]}")
    print(f"Cliente: {row[3]}")
    print(f"Grupo Veículo: {row[14]}")
    print(f"Data Pickup: {row[8]}")
    print(f"Data Dropoff: {row[10]}")
    
    # Calcular dias
    days = (row[10] - row[8]).days
    print(f"Dias de aluguer: {days}")
    
    print(f"Preço Total: {row[20]}")
    print(f"Depósito: {row[19]}")
    
    # Extras
    extras = row[15]
    print(f"\nExtras (raw): {extras}")
    if extras:
        try:
            extras_dict = json.loads(extras) if isinstance(extras, str) else extras
            print("\nExtras detalhados:")
            for key, value in extras_dict.items():
                print(f"  - {key}: {value}")
        except:
            print("  (Erro ao parsear extras)")
    
    print("\n" + "=" * 80)
    
    # Buscar configurações de preços para Grupo B, época média (março)
    cur.execute("SELECT key, value FROM admin_settings WHERE key LIKE 'commissioner_season_b_mid%' OR key LIKE 'commissioner_insurance_b_mid%' ORDER BY key")
    settings = cur.fetchall()
    
    print("\nCONFIGURAÇÕES DE PREÇOS (Grupo B, Época Média):")
    print("=" * 80)
    for key, value in settings:
        print(f"{key}: {value}")
    
    print("\n" + "=" * 80)

cur.close()
conn.close()
