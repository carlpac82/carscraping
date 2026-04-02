#!/usr/bin/env python3
"""
Script para executar migração do voucher_number para permitir NULL
"""
import os
import psycopg2
from urllib.parse import urlparse

def run_migration():
    """Permite NULL em voucher_number e cria índice UNIQUE parcial"""
    
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
        
        # Executar migração do voucher_number
        print("\n📝 Executando migração do voucher_number...")
        
        # Step 1: Drop existing UNIQUE constraint
        try:
            print("\n  Step 1: Removendo constraint UNIQUE...")
            cursor.execute("ALTER TABLE commission_bookings DROP CONSTRAINT IF EXISTS commission_bookings_voucher_number_key")
            conn.commit()
            print("  ✅ Constraint removida")
        except Exception as e:
            print(f"  ⚠️  Erro ao remover constraint: {e}")
        
        # Step 2: Drop NOT NULL constraint
        try:
            print("\n  Step 2: Permitindo valores NULL...")
            cursor.execute("ALTER TABLE commission_bookings ALTER COLUMN voucher_number DROP NOT NULL")
            conn.commit()
            print("  ✅ Coluna agora permite NULL")
        except Exception as e:
            print(f"  ❌ Erro ao permitir NULL: {e}")
            return False
        
        # Step 3: Create partial UNIQUE index
        try:
            print("\n  Step 3: Criando índice UNIQUE parcial...")
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS commission_bookings_voucher_number_unique 
                ON commission_bookings (voucher_number) 
                WHERE voucher_number IS NOT NULL
            """)
            conn.commit()
            print("  ✅ Índice UNIQUE parcial criado")
        except Exception as e:
            print(f"  ⚠️  Erro ao criar índice: {e}")
        
        print("\n✅ Migração concluída com sucesso!")
        
        # Verificar o estado da coluna
        cursor.execute("""
            SELECT 
                column_name, 
                is_nullable,
                data_type
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name = 'voucher_number'
        """)
        
        col_info = cursor.fetchone()
        if col_info:
            print(f"\n📋 Estado da coluna voucher_number:")
            print(f"  - Nome: {col_info[0]}")
            print(f"  - Nullable: {col_info[1]}")
            print(f"  - Tipo: {col_info[2]}")
        
        # Verificar índices
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'commission_bookings'
            AND indexname LIKE '%voucher%'
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print(f"\n📋 Índices relacionados com voucher_number:")
            for idx in indexes:
                print(f"  - {idx[0]}")
        
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
