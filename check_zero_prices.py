#!/usr/bin/env python3
import psycopg2
import sys

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Verificar reservas com price = 0
    cursor.execute("""
        SELECT id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time, price
        FROM commission_bookings
        WHERE price = 0 OR price IS NULL
        ORDER BY id DESC
        LIMIT 5
    """)
    
    bookings = cursor.fetchall()
    
    print("=== RESERVAS COM PREÇO = 0 ===")
    for booking in bookings:
        booking_id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time, price = booking
        print(f"ID: {booking_id}, Veículo: {vehicle_group}, Preço: {price}")
        print(f"  Levantamento: {pickup_date} {pickup_time}")
        print(f"  Entrega: {dropoff_date} {dropoff_time}")
        print()
    
    if not bookings:
        print("✅ Todas as reservas têm preço > 0")
    else:
        print(f"❌ Encontradas {len(bookings)} reservas com preço = 0")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
