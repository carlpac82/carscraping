#!/usr/bin/env python3
"""
Migra as tabelas que falharam na migração anterior
Foca nas mais importantes: recent_searches, vehicle_photos, automated_price_rules
"""
import psycopg2
import sys

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

CRITICAL_TABLES = [
    'recent_searches',
    'vehicle_photos', 
    'vehicle_images',
    'automated_price_rules',
    'system_logs',
    'whatsapp_config',
    'oauth_tokens',
    'inspection_photos',
]

print('🔧 MIGRANDO TABELAS PROBLEMÁTICAS')
print('=' * 70)

total_migrated = 0

for table_name in CRITICAL_TABLES:
    try:
        print(f'\n📦 {table_name}:', end=' ', flush=True)
        
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
        # Verificar se existe no Render
        render_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        if not render_cursor.fetchone()[0]:
            print('não existe no Render')
            continue
        
        # Contar registos
        render_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = render_cursor.fetchone()[0]
        
        if count == 0:
            print('vazia no Render')
            continue
        
        print(f'{count} registos...', end=' ', flush=True)
        
        # Obter estrutura
        render_cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns_info = render_cursor.fetchall()
        column_names = [col[0] for col in columns_info]
        column_types = {col[0]: col[1] for col in columns_info}
        
        # Verificar se tabela existe no Railway
        railway_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        
        if not railway_cursor.fetchone()[0]:
            # Criar tabela
            col_defs = []
            for col_name, col_type, nullable in columns_info:
                if 'character' in col_type or 'text' in col_type:
                    pg_type = 'TEXT'
                elif 'integer' in col_type or 'serial' in col_type or 'bigint' in col_type:
                    pg_type = 'BIGINT'
                elif 'boolean' in col_type:
                    pg_type = 'INTEGER'
                elif 'timestamp' in col_type:
                    pg_type = 'TIMESTAMP'
                elif 'date' in col_type:
                    pg_type = 'DATE'
                elif 'bytea' in col_type:
                    pg_type = 'BYTEA'
                elif 'numeric' in col_type or 'decimal' in col_type or 'real' in col_type:
                    pg_type = 'DECIMAL'
                else:
                    pg_type = 'TEXT'
                
                col_defs.append(f'"{col_name}" {pg_type}')
            
            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(col_defs)})'
            railway_cursor.execute(create_sql)
            railway_conn.commit()
        
        # Desativar triggers
        try:
            railway_cursor.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')
            railway_conn.commit()
        except:
            pass
        
        # Limpar
        railway_cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        railway_conn.commit()
        
        # Migrar dados - SEM foreign keys, apenas dados puros
        cols_quoted = ', '.join([f'"{col}"' for col in column_names])
        
        # Obter todos os dados
        render_cursor.execute(f'SELECT {cols_quoted} FROM "{table_name}"')
        rows = render_cursor.fetchall()
        
        inserted = 0
        errors = 0
        
        for row in rows:
            try:
                values = []
                for i, val in enumerate(row):
                    col_name = column_names[i]
                    col_type = column_types.get(col_name, '')
                    
                    if val is None:
                        values.append(None)
                    elif 'boolean' in col_type:
                        values.append(1 if val else 0)
                    elif 'bytea' in col_type and val:
                        # Manter dados binários
                        values.append(val)
                    else:
                        values.append(val)
                
                placeholders = ', '.join(['%s'] * len(values))
                insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
                railway_cursor.execute(insert_sql, values)
                inserted += 1
                
                if inserted % 100 == 0:
                    railway_conn.commit()
                    print(f'{inserted}...', end=' ', flush=True)
                    
            except Exception as e:
                errors += 1
                if errors > 10:
                    break
                continue
        
        railway_conn.commit()
        
        # Reativar triggers
        try:
            railway_cursor.execute(f'ALTER TABLE "{table_name}" ENABLE TRIGGER ALL')
            railway_conn.commit()
        except:
            pass
        
        if inserted > 0:
            print(f'✅ {inserted}/{count}')
            total_migrated += inserted
        else:
            print(f'❌ 0/{count} (erros: {errors})')
        
        render_cursor.close()
        render_conn.close()
        railway_cursor.close()
        railway_conn.close()
        
    except Exception as e:
        print(f'❌ {str(e)[:60]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass

print('\n' + '=' * 70)
print(f'✅ {total_migrated} registos adicionais migrados')
print('\n🌐 https://carscraping.up.railway.app')
