#!/usr/bin/env python3
"""
Script para desativar os grupos B1 e B2 na tabela car_groups
"""
import os
import psycopg2
from urllib.parse import urlparse

def disable_groups():
    """Desativa grupos B1 e B2"""
    
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
        
        # Desativar grupos B1 e B2
        print("\n📝 Desativando grupos B1 e B2...")
        
        cursor.execute("""
            UPDATE car_groups 
            SET enabled = 0 
            WHERE code IN ('B1', 'B2')
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        
        print(f"✅ {affected_rows} grupos desativados")
        
        # Verificar grupos ativos
        cursor.execute("""
            SELECT code, brand, model, enabled
            FROM car_groups
            WHERE code LIKE 'B%'
            ORDER BY code
        """)
        
        groups = cursor.fetchall()
        if groups:
            print(f"\n📋 Grupos que começam com B:")
            for group in groups:
                status = "✅ ATIVO" if group[3] else "❌ DESATIVADO"
                print(f"  - {group[0]} ({group[1]} {group[2]}): {status}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao desativar grupos: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = disable_groups()
    exit(0 if success else 1)
