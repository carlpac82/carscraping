#!/usr/bin/env python3
import psycopg2
import sys
from datetime import datetime

# Preços base por grupo de veículo (por dia)
BASE_PRICES = {
    'A': 25.0,    # KIA PICANTO
    'B': 30.0,    # Opel Corsa
    'C': 35.0,    # Fiat 500
    'D': 40.0,    # Renault Clio
    'E': 45.0,    # VW Polo
    'E1': 45.0,   # HYUNDAI i10
    'F': 50.0,    # Peugeot 208
    'G': 55.0,    # Toyota Yaris
    'H': 60.0,    # VW Golf
    'I': 65.0,    # Ford Focus
    'J': 70.0,    # Opel Astra
    'K': 75.0,    # Skoda Octavia
    'L': 80.0,    # VW Passat
    'M': 85.0,    # Ford Mondeo
    'N': 90.0,    # BMW Série 1
    'O': 95.0,    # Audi A3
    'P': 100.0,   # Mercedes Classe A
    'Q': 110.0,   # BMW Série 3
    'R': 120.0,   # Audi A4
    'S': 130.0,   # Mercedes Classe C
}

def calculate_days(pickup_date, pickup_time, dropoff_date, dropoff_time):
    """Calcular dias de aluguer (24h+1min = novo dia)"""
    pickup = datetime.strptime(f"{pickup_date} {pickup_time or '00:00'}", "%Y-%m-%d %H:%M:%S")
    dropoff = datetime.strptime(f"{dropoff_date} {dropoff_time or '00:00'}", "%Y-%m-%d %H:%M:%S")
    
    diff_ms = (dropoff - pickup).total_seconds() * 1000
    ms_per_day = 24 * 60 * 60 * 1000
    
    if diff_ms <= 0:
        return 0
    
    days = int(diff_ms / ms_per_day)
    if diff_ms % ms_per_day > 0:
        days += 1
    
    return days

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Obter reservas com preço = 0
    cursor.execute("""
        SELECT id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time
        FROM commission_bookings
        WHERE price = 0 OR price IS NULL
    """)
    
    bookings = cursor.fetchall()
    
    print(f"=== CORRIGINDO {len(bookings)} RESERVAS COM PREÇO = 0 ===")
    
    updated_count = 0
    for booking in bookings:
        booking_id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time = booking
        
        # Calcular dias
        days = calculate_days(pickup_date, pickup_time, dropoff_date, dropoff_time)
        
        # Obter preço base
        base_price = BASE_PRICES.get(vehicle_group, 40.0)  # Default 40€/dia
        
        # Calcular preço total
        total_price = base_price * days
        
        # Atualizar reserva
        cursor.execute("""
            UPDATE commission_bookings
            SET price = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (total_price, booking_id))
        
        print(f"✅ Reserva #{booking_id}: {vehicle_group} × {days} dias = {total_price:.2f}€")
        updated_count += 1
    
    if updated_count > 0:
        conn.commit()
        print(f"\n✅ {updated_count} reservas atualizadas com sucesso!")
    else:
        print("\n❌ Nenhuma reserva para atualizar")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
