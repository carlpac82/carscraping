#!/usr/bin/env python3
"""
Script para atualizar todos os comissionistas existentes para 20% de comissão
"""

import os
import sys
import logging

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_existing_commissioners():
    """Atualiza todos os comissionistas existentes para 20% de comissão"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela commissioners existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioners'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            logging.info("Tabela 'commissioners' não existe. Criando tabela...")
            
            # Criar tabela commissioners
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commissioners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    commission_rate DECIMAL(5, 2) DEFAULT 20.0,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    voucher_prefix VARCHAR(50),
                    phone VARCHAR(50),
                    default_location VARCHAR(255),
                    is_hotel BOOLEAN DEFAULT FALSE
                )
            """)
            
            logging.info("Tabela 'commissioners' criada com taxa padrão de 20%")
            conn.commit()
            return
        
        # Verificar comissionistas existentes
        cursor.execute("SELECT id, name, commission_rate FROM commissioners")
        commissioners = cursor.fetchall()
        
        if not commissioners:
            logging.info("Nenhum comissionista encontrado na base de dados")
            return
        
        logging.info(f"Encontrados {len(commissioners)} comissionistas")
        
        # Contar quantos estão com taxa diferente de 20%
        commissioners_to_update = []
        for comm_id, name, rate in commissioners:
            current_rate = float(rate) if rate else 15.0
            if abs(current_rate - 20.0) > 0.01:
                commissioners_to_update.append((comm_id, name, current_rate))
        
        if not commissioners_to_update:
            logging.info("Todos os comissionistas já estão com taxa de 20%")
            return
        
        logging.info(f"Atualizando {len(commissioners_to_update)} comissionistas para 20%:")
        
        for comm_id, name, current_rate in commissioners_to_update:
            logging.info(f"  - {name} (ID: {comm_id}): {current_rate}% -> 20%")
        
        # Atualizar todos para 20%
        cursor.execute("""
            UPDATE commissioners 
            SET commission_rate = 20.0,
                updated_at = CURRENT_TIMESTAMP
            WHERE commission_rate != 20.0 OR commission_rate IS NULL
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        logging.info(f"Successfully updated {updated_count} commissioners to 20% commission rate")
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM commissioners WHERE commission_rate = 20.0")
        verified_count = cursor.fetchone()[0]
        
        logging.info(f"Verified: {verified_count} commissioners now have 20% commission rate")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error updating commissioners: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    logging.info("Iniciando atualização de comissionistas existentes para 20%...")
    update_existing_commissioners()
    logging.info("Processo concluído.")

if __name__ == "__main__":
    main()
