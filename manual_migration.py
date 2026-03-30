#!/usr/bin/env python3
import psycopg2
import sys

# Conectar à base de dados
try:
    conn = psycopg2.connect(
        "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"
    )
    cursor = conn.cursor()
    
    print("=== EXECUTANDO MIGRAÇÃO DAS COLUNAS FALTANTES ===")
    
    # Adicionar coluna hotel
    try:
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS hotel VARCHAR(255)
        """)
        print("✅ Coluna 'hotel' adicionada com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao adicionar 'hotel': {e}")
    
    # Adicionar coluna room_number
    try:
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS room_number VARCHAR(50)
        """)
        print("✅ Coluna 'room_number' adicionada com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao adicionar 'room_number': {e}")
    
    # Adicionar coluna deposit
    try:
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS deposit DECIMAL(10, 2) DEFAULT 0.00
        """)
        print("✅ Coluna 'deposit' adicionada com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao adicionar 'deposit': {e}")
    
    # Fazer commit das alterações
    conn.commit()
    print("\n✅ Migration executada com sucesso!")
    
    # Verificar estrutura atualizada
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'commission_bookings'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\n=== ESTRUTURA ATUALIZADA ({len(columns)} colunas) ===")
    
    for col in columns:
        column_name, data_type = col
        print(f"{column_name:<20} {data_type}")
    
    # Verificar se as colunas foram adicionadas
    db_columns = [col[0] for col in columns]
    required_columns = ['hotel', 'room_number', 'deposit']
    
    print("\n=== VERIFICAÇÃO FINAL ===")
    for col in required_columns:
        status = "✅" if col in db_columns else "❌"
        print(f"{status} {col}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro geral: {e}")
    sys.exit(1)
