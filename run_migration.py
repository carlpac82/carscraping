#!/usr/bin/env python3
"""
Script para executar migração de campos de horários na tabela commissioners
"""
import os
import psycopg2
from urllib.parse import urlparse

def run_migration():
    """Adiciona campos de horários à tabela commissioners"""
    
    # Tentar obter DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no ambiente")
        print("Tentando ler do ficheiro .env ou configuração local...")
        
        # Tentar ler de ficheiro de configuração se existir
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not database_url:
        print("❌ Não foi possível obter DATABASE_URL")
        print("Por favor, define a variável de ambiente DATABASE_URL ou cria um ficheiro .env")
        return False
    
    # Parse da URL
    result = urlparse(database_url)
    
    try:
        # Conectar à base de dados
        print(f"🔌 Conectando a {result.hostname}...")
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        print("✅ Conectado à base de dados")
        
        # SQL de migração
        migrations = [
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
        
        print("\n📝 Executando migrações...")
        for column_name, column_def in migrations:
            try:
                sql = f"ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS {column_name} {column_def}"
                cursor.execute(sql)
                print(f"  ✅ {column_name}")
            except Exception as e:
                print(f"  ⚠️  {column_name}: {e}")
        
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        
        # Verificar se campos foram adicionados
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'commissioners' 
            AND column_name LIKE '%morning%' OR column_name LIKE '%afternoon%' OR column_name = 'time_interval_minutes'
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        if columns:
            print(f"\n📋 Campos adicionados ({len(columns)}):")
            for col in columns:
                print(f"  - {col[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao executar migração: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
