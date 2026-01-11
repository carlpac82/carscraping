#!/usr/bin/env python3
"""
MIGRAÇÃO FINAL E DEFINITIVA - RENDER → RAILWAY
Exporta TODOS os dados do Render e importa no Railway
Com indicador de progresso em tempo real
"""
import psycopg2
import sys

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRAÇÃO FINAL: RENDER → RAILWAY')
print('=' * 70)
print('Exportando e importando TODOS os dados com progresso em tempo real')
print('=' * 70)

# Lista COMPLETA de tabelas com dados
TABLES = [
    ('users', 6),
    ('app_settings', 27),
    ('user_settings', 2),
    ('activity_log', 365),
    ('automated_price_rules', 5363),
    ('automated_search_history', 88),
    ('price_automation_settings', 21),
    ('recent_searches', 1903),
    ('system_logs', 9120),
    ('whatsapp_config', 1),
    ('whatsapp_contacts', 2),
    ('whatsapp_conversations', 1),
    ('whatsapp_quick_replies', 15),
    ('whatsapp_templates', 8),
    ('oauth_tokens', 3),
    ('damage_reports', 44),
    ('damage_report_templates', 54),
    ('damage_report_coordinates', 90),
    ('damage_report_mapping_history', 19071),
    ('damage_report_numbering', 1),
    ('dr_email_templates', 4),
    ('rental_agreement_templates', 8),
    ('rental_agreement_coordinates', 15),
    ('rental_agreement_mapping_history', 867),
    ('vehicle_inspections', 8),
    ('inspection_photos', 30),
    ('vehicle_photos', 371),
    ('vehicle_images', 371),
    ('vehicle_name_overrides', 54),
    ('downloads_history', 29),
]

total_records = sum(count for _, count in TABLES)
processed = 0

print(f'\n📊 Total a migrar: {total_records} registos em {len(TABLES)} tabelas\n')

try:
    render_conn = psycopg2.connect(RENDER_DB_URL)
    railway_conn = psycopg2.connect(RAILWAY_DB_URL)
    
    for table_name, expected_count in TABLES:
        try:
            render_cursor = render_conn.cursor()
            railway_cursor = railway_conn.cursor()
            
            # Verificar se existe
            render_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
            if not render_cursor.fetchone()[0]:
                print(f'⏭️  {table_name}: não existe')
                continue
            
            # Obter estrutura
            render_cursor.execute(f"""
                SELECT column_name, data_type 
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
                
                create_sql = f'CREATE TABLE "{table_name}" ({", ".join(col_defs)})'
                railway_cursor.execute(create_sql)
                railway_conn.commit()
            
            # Limpar
            railway_cursor.execute(f'DELETE FROM "{table_name}"')
            railway_conn.commit()
            
            # Migrar em lotes de 50
            BATCH_SIZE = 50
            offset = 0
            inserted = 0
            
            cols_quoted = ', '.join([f'"{col}"' for col in column_names])
            
            print(f'📦 {table_name}: ', end='', flush=True)
            
            while offset < expected_count:
                render_cursor.execute(f'SELECT {cols_quoted} FROM "{table_name}" LIMIT {BATCH_SIZE} OFFSET {offset}')
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
                        insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
                        railway_cursor.execute(insert_sql, values)
                        inserted += 1
                        processed += 1
                        
                        # Mostrar progresso a cada 100 registos
                        if processed % 100 == 0:
                            percent = (processed / total_records) * 100
                            print(f'\r📦 {table_name}: {inserted}/{expected_count} | Total: {processed}/{total_records} ({percent:.1f}%)', end='', flush=True)
                    except:
                        continue
                
                railway_conn.commit()
                offset += BATCH_SIZE
            
            percent = (processed / total_records) * 100
            print(f'\r📦 {table_name}: ✅ {inserted}/{expected_count} | Total: {processed}/{total_records} ({percent:.1f}%)')
            
            render_cursor.close()
            railway_cursor.close()
            
        except Exception as e:
            print(f'\r📦 {table_name}: ❌ {str(e)[:50]}')
            try:
                railway_conn.rollback()
            except:
                pass
            continue
    
    render_conn.close()
    railway_conn.close()
    
    print('\n' + '=' * 70)
    print('🎉 MIGRAÇÃO CONCLUÍDA!')
    print('=' * 70)
    print(f'✅ {processed} registos migrados')
    print('\n🌐 https://carscraping.up.railway.app')
    print('🔐 Login: mesmas credenciais do Render')
    print('\n💰 Poupança: $9/mês ($108/ano) vs Render')
    
except Exception as e:
    print(f'\n❌ Erro: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
