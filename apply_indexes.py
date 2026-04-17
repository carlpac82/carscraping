#!/usr/bin/env python3
"""
Script para aplicar índices de performance no PostgreSQL
Executa automaticamente ao iniciar a aplicação
100% SEGURO - apenas adiciona índices, não altera dados
"""

import os
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def apply_indexes():
    """Aplica índices de performance no PostgreSQL"""
    
    # Ler DATABASE_URL (usado pela aplicação principal)
    database_url = os.getenv('DATABASE_URL')
    
    # Verificar se DATABASE_URL está definido e é PostgreSQL
    if not database_url:
        return
    
    if not (database_url.startswith('postgresql://') or database_url.startswith('postgres://')):
        return
    
    try:
        # Conectar ao banco usando DATABASE_URL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logging.info("=" * 80)
        logging.info("🚀 APPLYING PERFORMANCE INDEXES")
        logging.info("=" * 80)
        
        # Ler SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'create_indexes.sql')
        
        if not os.path.exists(sql_file):
            logging.warning(f"⚠️ SQL file not found: {sql_file}")
            return
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Executar SQL
        cursor.execute(sql_content)
        conn.commit()
        
        # Contar índices criados
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
        """)
        index_count = cursor.fetchone()[0]
        
        logging.info(f"✅ Performance indexes applied successfully")
        logging.info(f"📊 Total indexes: {index_count}")
        logging.info("=" * 80)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"❌ Error applying indexes: {str(e)}")
        logging.error(f"   This is not critical - app will continue to work")

if __name__ == "__main__":
    apply_indexes()
