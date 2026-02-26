#!/usr/bin/env python3
"""Script para adicionar coluna updated_by à tabela current_prices"""

import psycopg2
import os

# Conectar ao PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:aMXjJxPXTAVZLvMYVCQqhZXNQMlkGXQV@shortline.proxy.rlwy.net:52815/railway')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Verificar se coluna já existe
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'current_prices' 
        AND column_name = 'updated_by'
    """)
    
    if cur.fetchone():
        print("✅ Coluna updated_by já existe")
    else:
        print("➕ Adicionando coluna updated_by...")
        cur.execute("ALTER TABLE current_prices ADD COLUMN updated_by TEXT")
        conn.commit()
        print("✅ Coluna updated_by adicionada com sucesso")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
