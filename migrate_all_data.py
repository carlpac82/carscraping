#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🔄 MIGRAÇÃO COMPLETA: RENDER → RAILWAY')
print('=' * 60)

# Tabelas prioritárias (ordem importa)
PRIORITY_TABLES = [
    'users',
    'user_settings',
    'app_settings',
    'recent_searches',
    'automated_search_history',
    'automated_price_rules',
    'price_automation_settings',
    'system_logs',
    'activity_log',
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
    'rental_agreement_templates',
    'rental_agreement_coordinates',
    'rental_agreement_mapping_history',
    'vehicle_inspections',
    'inspection_photos',
    'vehicle_photos',
    'vehicle_images',
    'vehicle_name_overrides',
    'downloads_history',
    'dr_email_templates',
]

try:
    render_conn = psycopg2.connect(RENDER_DB_URL)
    render_cursor = render_conn.cursor(cursor_factory=RealDictCursor)
    
    railway_conn = psycopg2.connect(RAILWAY_DB_URL)
    railway_conn.autocommit = False
    railway_cursor = railway_conn.cursor()
    
    total_rows = 0
    migrated_tables = 0
    
    for table in PRIORITY_TABLES:
        try:
            # Verificar se existe no Render
            render_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            if not render_cursor.fetchone()[0]:
                continue
            
            # Contar registos
            render_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = render_cursor.fetchone()[0]
            
            if count == 0:
                continue
            
            print(f'\n📦 {table}: {count} registos')
            
            # Obter dados
            render_cursor.execute(f'SELECT * FROM "{table}"')
            rows = render_cursor.fetchall()
            
            if not rows:
                continue
            
            # Verificar se tabela existe no Railway
            railway_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            table_exists = railway_cursor.fetchone()[0]
            
            if not table_exists:
                print(f'   ⚠️  Tabela não existe no Railway, criando...')
                # Obter CREATE TABLE do Render
                render_cursor.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns_info = render_cursor.fetchall()
                
                # Criar tabela básica
                create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ('
                col_defs = []
                for col in columns_info:
                    col_name = col['column_name']
                    col_type = col['data_type']
                    
                    # Mapear tipos
                    if col_type == 'character varying':
                        col_type = 'TEXT'
                    elif col_type == 'integer':
                        col_type = 'INTEGER'
                    elif col_type == 'timestamp without time zone':
                        col_type = 'TIMESTAMP'
                    elif col_type == 'boolean':
                        col_type = 'BOOLEAN'
                    elif col_type == 'bytea':
                        col_type = 'BYTEA'
                    
                    col_defs.append(f'"{col_name}" {col_type}')
                
                create_sql += ', '.join(col_defs) + ')'
                railway_cursor.execute(create_sql)
                railway_conn.commit()
            
            # Limpar tabela
            railway_cursor.execute(f'DELETE FROM "{table}"')
            
            # Inserir dados
            columns = list(rows[0].keys())
            columns_str = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))
            
            inserted = 0
            for row in rows:
                try:
                    values = [row[col] for col in columns]
                    insert_sql = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'
                    railway_cursor.execute(insert_sql, values)
                    inserted += 1
                except Exception as e:
                    print(f'   ⚠️  Erro ao inserir registo: {str(e)[:50]}...')
                    continue
            
            railway_conn.commit()
            total_rows += inserted
            migrated_tables += 1
            print(f'   ✅ {inserted} registos migrados')
            
        except Exception as e:
            print(f'   ❌ Erro: {str(e)[:100]}')
            railway_conn.rollback()
            continue
    
    render_cursor.close()
    render_conn.close()
    railway_cursor.close()
    railway_conn.close()
    
    print('\n' + '=' * 60)
    print(f'✅ MIGRAÇÃO CONCLUÍDA!')
    print(f'📊 {migrated_tables} tabelas migradas')
    print(f'📊 {total_rows} registos totais migrados')
    print('\n🎉 Dados transferidos para Railway!')
    print('\nPodes fazer login em: https://carscraping.up.railway.app')
    print('Credenciais: as mesmas do Render')
    
except Exception as e:
    print(f'\n❌ Erro: {e}')
    import traceback
    traceback.print_exc()
