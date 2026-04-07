#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

def add_can_manage_commissioners_column():
    load_dotenv()
    
    # Usar DATABASE_URL do .env
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL não encontrada no .env")
        return False
    
    try:
        # Conectar à base de dados
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'can_manage_commissioners'
        """)
        
        if cursor.fetchone():
            print("A coluna 'can_manage_commissioners' já existe na tabela users")
            return True
        
        # Adicionar a coluna
        print("A adicionar coluna 'can_manage_commissioners' à tabela users...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN can_manage_commissioners BOOLEAN DEFAULT FALSE
        """)
        
        # Adicionar comentário
        cursor.execute("""
            COMMENT ON COLUMN users.can_manage_commissioners 
            IS 'Determines if user can manage commissioners (only for support role)'
        """)
        
        conn.commit()
        print("Coluna 'can_manage_commissioners' adicionada com sucesso!")
        
        # Verificar se foi adicionada
        cursor.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'can_manage_commissioners'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Coluna verificada: {result[0]} ({result[1]}) default: {result[2]}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_can_manage_commissioners_column()
