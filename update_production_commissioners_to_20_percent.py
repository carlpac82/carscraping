#!/usr/bin/env python3
"""
Script para atualizar todos os comissionistas em produção para 20% de comissão
Este script será executado via API endpoint para atualizar a base de dados em produção
"""

import os
import sys
import logging
import requests

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_production_commissioners():
    """Atualiza todos os comissionistas para 20% de comissão"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verificar quantos comissionistas existem
        cursor.execute("SELECT COUNT(*) FROM commissioners")
        total_count = cursor.fetchone()[0]
        
        logging.info(f"Total de comissionistas na base de dados: {total_count}")
        
        if total_count == 0:
            logging.warning("Nenhum comissionista encontrado na base de dados")
            return False
        
        # Verificar quantos já estão com 20%
        cursor.execute("SELECT COUNT(*) FROM commissioners WHERE commission_rate = 20")
        already_20_count = cursor.fetchone()[0]
        
        logging.info(f"Comissionistas já com 20%: {already_20_count}")
        
        # Verificar quantos estão com 15%
        cursor.execute("SELECT COUNT(*) FROM commissioners WHERE commission_rate = 15")
        with_15_count = cursor.fetchone()[0]
        
        logging.info(f"Comissionistas com 15%: {with_15_count}")
        
        if with_15_count == 0:
            logging.info("Todos os comissionistas já estão com 20%!")
            return True
        
        # Atualizar todos os comissionistas para 20%
        cursor.execute("""
            UPDATE commissioners 
            SET commission_rate = 20, updated_at = CURRENT_TIMESTAMP
            WHERE commission_rate != 20
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        logging.info(f"Atualizados {updated_count} comissionistas para 20%")
        
        # Verificar resultado final
        cursor.execute("SELECT COUNT(*) FROM commissioners WHERE commission_rate = 20")
        final_20_count = cursor.fetchone()[0]
        
        logging.info(f"Total final com 20%: {final_20_count}")
        
        return updated_count > 0
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao atualizar comissionistas: {e}")
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    logging.info("Iniciando atualização de comissionistas para 20%...")
    
    success = update_production_commissioners()
    
    if success:
        logging.info("Atualização concluída com sucesso!")
    else:
        logging.error("Falha na atualização dos comissionistas")

if __name__ == "__main__":
    main()
