#!/usr/bin/env python3
"""
Script para adicionar campos de configuração de horários à tabela commissioners
"""
import os
import psycopg2
from urllib.parse import urlparse

def add_schedule_fields():
    """Adiciona campos de horários à tabela commissioners"""
    
    # Obter DATABASE_URL do ambiente
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    # Parse da URL
    result = urlparse(database_url)
    
    try:
        # Conectar à base de dados
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        print("✅ Conectado à base de dados")
        
        # Adicionar colunas se não existirem
        columns_to_add = [
            ("weekday_start_morning", "TIME DEFAULT '09:30'"),
            ("weekday_end_morning", "TIME DEFAULT '12:30'"),
            ("weekday_start_afternoon", "TIME DEFAULT '15:00'"),
            ("weekday_end_afternoon", "TIME DEFAULT '17:00'"),
            ("sunday_start_morning", "TIME DEFAULT '09:30'"),
            ("sunday_end_morning", "TIME DEFAULT '12:30'"),
            ("sunday_start_afternoon", "TIME DEFAULT '15:30'"),
            ("sunday_end_afternoon", "TIME DEFAULT '17:00'"),
            ("time_interval_minutes", "INTEGER DEFAULT 15")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                cursor.execute(f"""
                    ALTER TABLE commissioners 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_def}
                """)
                print(f"✅ Coluna {column_name} adicionada")
            except Exception as e:
                print(f"⚠️  Coluna {column_name}: {e}")
        
        conn.commit()
        print("\n✅ Campos de horários adicionados com sucesso!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    add_schedule_fields()
