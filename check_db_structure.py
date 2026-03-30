#!/usr/bin/env python3
import psycopg2
import sys

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    # Obter informação sobre a tabela commission_bookings
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'commission_bookings'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print("=== ESTRUTURA DA TABELA commission_bookings ===")
    print(f"{'Coluna':<20} {'Tipo':<20} {'Nulo?':<8} {'Default':<15}")
    print("-" * 70)
    
    for col in columns:
        column_name, data_type, is_nullable, column_default = col
        default = str(column_default) if column_default else "NULL"
        print(f"{column_name:<20} {data_type:<20} {is_nullable:<8} {default:<15}")
    
    print(f"\nTotal de colunas: {len(columns)}")
    
    # Verificar também o que o frontend está a enviar
    print("\n=== CAMPOS ENVIADOS PELO FRONTEND ===")
    frontend_fields = [
        'client_name', 'client_email', 'client_phone', 'hotel', 'room_number',
        'pickup_date', 'pickup_time', 'dropoff_date', 'dropoff_time',
        'pickup_location', 'dropoff_location', 'flight_number', 'language',
        'observations', 'deposit', 'price', 'extras'
    ]
    
    db_columns = [col[0] for col in columns]
    
    for field in frontend_fields:
        status = "✅" if field in db_columns else "❌"
        print(f"{status} {field}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
