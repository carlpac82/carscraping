#!/usr/bin/env python3
"""
Script para migrar preços antigos para o novo schema com day_start/day_end
"""
import os
import psycopg2
from urllib.parse import urlparse

# Conectar ao Railway PostgreSQL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL não encontrada")
    exit(1)

# Parse URL
url = urlparse(database_url)

conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    user=url.username,
    password=url.password,
    database=url.path[1:]
)

print("✅ Conectado ao PostgreSQL")

try:
    with conn.cursor() as cur:
        # Verificar registos sem day_start/day_end
        cur.execute("""
            SELECT COUNT(*) 
            FROM current_prices 
            WHERE day_start IS NULL OR day_end IS NULL
        """)
        count = cur.fetchone()[0]
        print(f"📊 Encontrados {count} registos sem day_start/day_end")
        
        if count > 0:
            # Atualizar registos antigos
            cur.execute("""
                UPDATE current_prices 
                SET day_start = 1, day_end = 31 
                WHERE day_start IS NULL OR day_end IS NULL
            """)
            conn.commit()
            print(f"✅ Atualizados {count} registos com day_start=1, day_end=31")
        
        # Verificar duplicados (mesmo location/month/year mas diferentes períodos)
        cur.execute("""
            SELECT location, month, year, COUNT(*) as cnt
            FROM current_prices
            GROUP BY location, month, year
            HAVING COUNT(*) > 1
        """)
        duplicates = cur.fetchall()
        
        if duplicates:
            print(f"⚠️  Encontrados {len(duplicates)} meses com múltiplos períodos:")
            for dup in duplicates:
                print(f"   - {dup[0]}, {dup[1]}/{dup[2]}: {dup[3]} períodos")
        
        # Mostrar total de registos
        cur.execute("SELECT COUNT(*) FROM current_prices")
        total = cur.fetchone()[0]
        print(f"📊 Total de {total} registos na tabela current_prices")
        
        # Mostrar alguns exemplos
        cur.execute("""
            SELECT location, month, year, day_start, day_end 
            FROM current_prices 
            ORDER BY location, year, month, day_start
            LIMIT 10
        """)
        examples = cur.fetchall()
        print("\n📋 Exemplos de registos:")
        for ex in examples:
            print(f"   {ex[0]}, {ex[1]}/{ex[2]}, dias {ex[3]}-{ex[4]}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    conn.rollback()
finally:
    conn.close()
    print("\n✅ Migração concluída")
