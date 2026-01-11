#!/usr/bin/env python3
import psycopg2
import time

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

# Tabelas restantes (as que falharam)
TABLES = [
    'recent_searches',
    'automated_search_history',
    'automated_price_rules',
    'system_logs',
    'whatsapp_config',
    'whatsapp_contacts',
    'whatsapp_conversations',
    'whatsapp_quick_replies',
    'whatsapp_templates',
    'oauth_tokens',
    'damage_reports',
    'damage_report_templates',
    'damage_report_coordinates',
    'damage_report_mapping_history',
    'damage_report_numbering',
    'dr_email_templates',
    'rental_agreement_templates',
    'rental_agreement_coordinates',
    'rental_agreement_mapping_history',
    'vehicle_inspections',
    'inspection_photos',
    'vehicle_photos',
    'vehicle_images',
    'vehicle_name_overrides',
    'downloads_history',
]

print('🚀 MIGRAÇÃO EM LOTES')
print('=' * 60)

total_migrated = 0

for table in TABLES:
    try:
        # Nova conexão para cada tabela
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
        # Verificar se existe
        render_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
        if not render_cursor.fetchone()[0]:
            print(f'⏭️  {table}: não existe')
            render_conn.close()
            railway_conn.close()
            continue
        
        # Contar
        render_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = render_cursor.fetchone()[0]
        
        if count == 0:
            print(f'⏭️  {table}: vazia')
            render_conn.close()
            railway_conn.close()
            continue
        
        print(f'📦 {table}: {count} registos...', end='', flush=True)
        
        # Obter estrutura
        render_cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        columns_info = render_cursor.fetchall()
        column_names = [col[0] for col in columns_info]
        column_types = {col[0]: col[1] for col in columns_info}
        
        # Verificar se tabela existe no Railway
        railway_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
        
        if not railway_cursor.fetchone()[0]:
            # Criar tabela
            col_defs = []
            for col_name, col_type in columns_info:
                if 'character' in col_type or 'text' in col_type:
                    pg_type = 'TEXT'
                elif 'integer' in col_type or 'serial' in col_type:
                    pg_type = 'INTEGER'
                elif 'boolean' in col_type:
                    pg_type = 'INTEGER'
                elif 'timestamp' in col_type:
                    pg_type = 'TIMESTAMP'
                elif 'date' in col_type:
                    pg_type = 'DATE'
                elif 'bytea' in col_type:
                    pg_type = 'BYTEA'
                elif 'numeric' in col_type or 'decimal' in col_type:
                    pg_type = 'DECIMAL'
                else:
                    pg_type = 'TEXT'
                
                col_defs.append(f'"{col_name}" {pg_type}')
            
            create_sql = f'CREATE TABLE "{table}" ({", ".join(col_defs)})'
            railway_cursor.execute(create_sql)
            railway_conn.commit()
        
        # Limpar
        railway_cursor.execute(f'DELETE FROM "{table}"')
        railway_conn.commit()
        
        # Migrar em lotes de 100
        BATCH_SIZE = 100
        offset = 0
        inserted = 0
        
        cols_quoted = ', '.join([f'"{col}"' for col in column_names])
        
        while offset < count:
            render_cursor.execute(f'SELECT {cols_quoted} FROM "{table}" LIMIT {BATCH_SIZE} OFFSET {offset}')
            rows = render_cursor.fetchall()
            
            if not rows:
                break
            
            for row in rows:
                try:
                    values = list(row)
                    for i, col_name in enumerate(column_names):
                        if column_types[col_name] == 'boolean':
                            values[i] = 1 if values[i] else 0
                    
                    placeholders = ', '.join(['%s'] * len(values))
                    insert_sql = f'INSERT INTO "{table}" ({cols_quoted}) VALUES ({placeholders})'
                    railway_cursor.execute(insert_sql, values)
                    inserted += 1
                except:
                    continue
            
            railway_conn.commit()
            offset += BATCH_SIZE
        
        total_migrated += inserted
        print(f' ✅ {inserted}')
        
        render_cursor.close()
        render_conn.close()
        railway_cursor.close()
        railway_conn.close()
        
        time.sleep(0.5)  # Pequena pausa entre tabelas
        
    except Exception as e:
        print(f' ❌ {str(e)[:50]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass
        continue

print('\n' + '=' * 60)
print(f'✅ MIGRAÇÃO CONCLUÍDA!')
print(f'📊 {total_migrated} registos migrados')
print('\n🌐 https://carscraping.up.railway.app')
