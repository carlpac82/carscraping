#!/usr/bin/env python3
"""
Adicionar colunas de assinatura à tabela commission_bookings
"""
import psycopg2
import os

def run_migration():
    """Adicionar colunas commission_signature e commission_receiver_name"""
    
    # Obter DATABASE_URL do ambiente
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no ambiente")
        print("Tentando ler do ficheiro .env...")
        
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
        return False
    
    try:
        print("🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("📝 Adicionando colunas de assinatura...")
        
        # Adicionar coluna commission_signature
        cur.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS commission_signature TEXT;
        """)
        
        # Adicionar coluna commission_receiver_name
        cur.execute("""
            ALTER TABLE commission_bookings 
            ADD COLUMN IF NOT EXISTS commission_receiver_name VARCHAR(255);
        """)
        
        conn.commit()
        
        print("✅ Colunas adicionadas com sucesso!")
        
        # Verificar se as colunas foram criadas
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name IN ('commission_signature', 'commission_receiver_name')
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        print("\n📋 Colunas criadas:")
        for col_name, col_type in columns:
            print(f"   - {col_name}: {col_type}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("MIGRAÇÃO: Adicionar colunas de assinatura")
    print("=" * 80)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("✅ Migração concluída com sucesso!")
    else:
        print("❌ Migração falhou!")
    print("=" * 80)
