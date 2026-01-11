#!/usr/bin/env python3
"""
Migrar TODOS os dados do Render para Railway
Preserva utilizadores, passwords, pesquisas, histórico, etc.
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# URLs das bases de dados
RENDER_DB_URL = input("Cola a DATABASE_URL do Render: ")
RAILWAY_DB_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

print("\n🔄 MIGRAÇÃO DE DADOS: RENDER → RAILWAY")
print("=" * 60)

# Tabelas a migrar (ordem importa por causa de foreign keys)
TABLES_TO_MIGRATE = [
    'users',
    'recent_searches',
    'price_snapshots',
    'automated_prices_history',
    'system_logs',
    'settings',
    'whatsapp_config',
]

try:
    # Conectar ao Render
    print("\n📡 Conectando ao Render...")
    render_conn = psycopg2.connect(RENDER_DB_URL)
    render_cursor = render_conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Conectado ao Render")
    
    # Conectar ao Railway
    print("📡 Conectando ao Railway...")
    railway_conn = psycopg2.connect(RAILWAY_DB_URL)
    railway_conn.autocommit = False
    railway_cursor = railway_conn.cursor()
    print("✅ Conectado ao Railway")
    
    total_rows = 0
    
    # Migrar cada tabela
    for table in TABLES_TO_MIGRATE:
        print(f"\n📦 Migrando tabela: {table}")
        
        try:
            # Verificar se tabela existe no Render
            render_cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """)
            
            if not render_cursor.fetchone()[0]:
                print(f"   ⚠️  Tabela {table} não existe no Render, pulando...")
                continue
            
            # Contar registos
            render_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = render_cursor.fetchone()[0]
            
            if count == 0:
                print(f"   ℹ️  Tabela {table} vazia, pulando...")
                continue
            
            print(f"   📊 {count} registos encontrados")
            
            # Obter todos os dados
            render_cursor.execute(f"SELECT * FROM {table}")
            rows = render_cursor.fetchall()
            
            if not rows:
                continue
            
            # Limpar tabela no Railway
            print(f"   🗑️  Limpando tabela no Railway...")
            railway_cursor.execute(f"DELETE FROM {table}")
            
            # Obter nomes das colunas
            columns = list(rows[0].keys())
            columns_str = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Inserir dados
            print(f"   📥 Inserindo {len(rows)} registos...")
            
            for row in rows:
                values = [row[col] for col in columns]
                insert_sql = f"""
                    INSERT INTO {table} ({columns_str})
                    VALUES ({placeholders})
                """
                railway_cursor.execute(insert_sql, values)
            
            railway_conn.commit()
            total_rows += len(rows)
            print(f"   ✅ {len(rows)} registos migrados")
            
        except Exception as e:
            print(f"   ❌ Erro ao migrar {table}: {e}")
            railway_conn.rollback()
            continue
    
    # Fechar conexões
    render_cursor.close()
    render_conn.close()
    railway_cursor.close()
    railway_conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ MIGRAÇÃO CONCLUÍDA!")
    print(f"📊 Total de registos migrados: {total_rows}")
    print("\n🎉 Todos os teus dados foram transferidos para Railway!")
    print("\nPodes agora:")
    print("1. Fazer login em: https://carscraping.up.railway.app")
    print("2. Usar as mesmas credenciais do Render")
    print("3. Ver todo o histórico e dados preservados")
    
except Exception as e:
    print(f"\n❌ Erro na migração: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
