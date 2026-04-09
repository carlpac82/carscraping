#!/usr/bin/env python3
"""
Script para adicionar campo dropoff_date à tabela commission_bookings
"""

import os
import sys
import logging

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def add_dropoff_date_column():
    """Adiciona coluna dropoff_date à tabela commission_bookings"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(commission_bookings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'dropoff_date' in column_names:
            logging.info("Coluna 'dropoff_date' já existe na tabela commission_bookings")
            return
        
        logging.info("Adicionando coluna 'dropoff_date' à tabela commission_bookings...")
        
        # Adicionar coluna dropoff_date
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN dropoff_date DATETIME
        """)
        
        conn.commit()
        logging.info("Coluna 'dropoff_date' adicionada com sucesso!")
        
        # Calcular dropoff_date para registros existentes (pickup_date + days)
        logging.info("Calculando dropoff_date para registros existentes...")
        
        cursor.execute("""
            UPDATE commission_bookings 
            SET dropoff_date = date(pickup_date, '+' || CAST(days AS INTEGER) || ' days')
            WHERE pickup_date IS NOT NULL 
            AND days IS NOT NULL 
            AND dropoff_date IS NULL
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        logging.info(f"Calculado dropoff_date para {updated_count} registros!")
        
        # Verificar resultado
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN dropoff_date IS NOT NULL THEN 1 END) as with_dropoff
            FROM commission_bookings
        """)
        
        result = cursor.fetchone()
        total_count, with_dropoff_count = result
        
        logging.info(f"Total de registros: {total_count}")
        logging.info(f"Registros com dropoff_date: {with_dropoff_count}")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao adicionar coluna dropoff_date: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    logging.info("Iniciando adição de coluna dropoff_date...")
    add_dropoff_date_column()
    logging.info("Processo concluído.")

if __name__ == "__main__":
    main()
