#!/usr/bin/env python3
import psycopg2
import sys

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Apagar a reserva #1
    cursor.execute("DELETE FROM commission_bookings WHERE id = 1")
    
    rows_affected = cursor.rowcount
    conn.commit()
    
    if rows_affected > 0:
        print(f"✅ Reserva #1 apagada com sucesso!")
    else:
        print("❌ Reserva #1 não encontrada")
    
    # Verificar se há mais reservas
    cursor.execute("SELECT COUNT(*) FROM commission_bookings")
    count = cursor.fetchone()[0]
    
    print(f"\n📊 Total de reservas restantes: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
