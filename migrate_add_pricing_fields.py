#!/usr/bin/env python3
"""
Migration: Adicionar campos de preços discriminados à tabela commission_bookings
"""
import psycopg2
import os

def run_migration():
    """Adiciona colunas de preços discriminados"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada. Execute em produção ou defina a variável.")
        return
    
    # Fix para Railway/Render que usam postgres:// em vez de postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        print("🔄 Adicionando colunas de preços discriminados...")
        
        # Adicionar colunas se não existirem
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS base_price DECIMAL(10, 2) DEFAULT 0.00,
            ADD COLUMN IF NOT EXISTS premium_insurance DECIMAL(10, 2) DEFAULT 0.00,
            ADD COLUMN IF NOT EXISTS road_tax DECIMAL(10, 2) DEFAULT 0.00,
            ADD COLUMN IF NOT EXISTS extras_total DECIMAL(10, 2) DEFAULT 0.00,
            ADD COLUMN IF NOT EXISTS rental_days INTEGER DEFAULT 0
        """)
        
        conn.commit()
        print("✅ Colunas adicionadas com sucesso!")
        
        # Verificar as colunas
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name IN ('base_price', 'premium_insurance', 'road_tax', 'extras_total', 'rental_days')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Colunas na tabela:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
