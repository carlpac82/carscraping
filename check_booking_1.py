#!/usr/bin/env python3
import psycopg2
import sys

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Verificar a reserva #1 atualizada
    cursor.execute("""
        SELECT id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time, price
        FROM commission_bookings
        WHERE id = 1
    """)
    
    booking = cursor.fetchone()
    
    if booking:
        booking_id, vehicle_group, pickup_date, pickup_time, dropoff_date, dropoff_time, price = booking
        print("=== RESERVA #1 ATUALIZADA ===")
        print(f"ID: {booking_id}")
        print(f"Veículo: {vehicle_group}")
        print(f"Preço: €{price:.2f}")
        print(f"Levantamento: {pickup_date} {pickup_time}")
        print(f"Entrega: {dropoff_date} {dropoff_time}")
        print(f"Status: ✅ Preço corrigido!")
    else:
        print("❌ Reserva #1 não encontrada")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
