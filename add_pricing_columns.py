#!/usr/bin/env python3
"""
Script para adicionar colunas de preços discriminados à tabela commission_bookings
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

def add_pricing_columns():
    """Adiciona colunas de preços discriminados à tabela commission_bookings"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        print("Adicionando colunas de preços discriminados...")
        
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
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name IN ('base_price', 'premium_insurance', 'road_tax', 'extras_total', 'rental_days')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        print("\nColunas adicionadas:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_pricing_columns()
