#!/usr/bin/env python3
"""
Script para adicionar colunas de schedule à tabela commissioners
Execute este script para corrigir o erro: column "weekday_start_morning" does not exist
"""

import os
import psycopg2
from urllib.parse import urlparse

def migrate_schedule_columns():
    # Obter DATABASE_URL do ambiente ou usar valor padrão
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL não encontrada nas variáveis de ambiente")
        print("\nPara executar este script:")
        print("1. Obtenha a DATABASE_URL do Railway")
        print("2. Execute: export DATABASE_URL='postgresql://...'")
        print("3. Execute novamente este script: python migrate_schedule_columns.py")
        return False
    
    # Parse da URL
    result = urlparse(database_url)
    
    print("🔄 Conectando à base de dados...")
    print(f"   Host: {result.hostname}")
    print(f"   Database: {result.path[1:]}")
    
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
        
        print("\n✅ Conectado com sucesso!")
        print("\n🔧 Adicionando colunas de schedule...")
        
        # Lista de colunas para adicionar
        columns = [
            ("weekday_start_morning", "TIME", "'09:30'"),
            ("weekday_end_morning", "TIME", "'12:30'"),
            ("weekday_start_afternoon", "TIME", "'15:00'"),
            ("weekday_end_afternoon", "TIME", "'17:00'"),
            ("sunday_start_morning", "TIME", "'09:30'"),
            ("sunday_end_morning", "TIME", "'12:30'"),
            ("sunday_start_afternoon", "TIME", "'15:30'"),
            ("sunday_end_afternoon", "TIME", "'17:00'"),
            ("time_interval_minutes", "INTEGER", "15")
        ]
        
        for col_name, col_type, default_value in columns:
            try:
                sql = f"ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS {col_name} {col_type} DEFAULT {default_value};"
                cursor.execute(sql)
                print(f"   ✓ {col_name}")
            except Exception as e:
                print(f"   ⚠️  {col_name}: {str(e)}")
        
        # Commit das alterações
        conn.commit()
        
        print("\n✅ Migração concluída com sucesso!")
        print("\n📊 Verificando colunas adicionadas...")
        
        # Verificar se as colunas foram adicionadas
        cursor.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'commissioners' 
            AND column_name LIKE '%start%' OR column_name LIKE '%end%' OR column_name = 'time_interval_minutes'
            ORDER BY column_name;
        """)
        
        results = cursor.fetchall()
        if results:
            print("\nColunas encontradas:")
            for row in results:
                print(f"   • {row[0]} ({row[1]}) = {row[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Tudo pronto! O erro 'weekday_start_morning does not exist' deve estar resolvido.")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao executar migração: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  MIGRAÇÃO: Adicionar Colunas de Schedule")
    print("=" * 60)
    migrate_schedule_columns()
