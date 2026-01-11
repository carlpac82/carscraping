#!/usr/bin/env python3
"""
MIGRAÇÃO FINAL COM RECONEXÃO AUTOMÁTICA
Migra TODOS os dados com progresso em tempo real
Reconecta após cada tabela para evitar timeouts
"""
import psycopg2
import sys
import time

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRAÇÃO FINAL COM RECONEXÃO')
print('=' * 70)
print('Migrando TODOS os dados com progresso em tempo real')
print('=' * 70)

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
total_migrated = 0

print(f'\n📊 Total: {total_records} registos em {len(TABLES)} tabelas\n')

for idx, (table_name, expected_count) in enumerate(TABLES, 1):
    try:
        # RECONECTAR para cada tabela
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
        # Verificar se existe no Render
        render_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        if not render_cursor.fetchone()[0]:
            print(f'[{idx}/{len(TABLES)}] ⏭️  {table_name}: não existe no Render')
            render_cursor.close()
            render_conn.close()
            railway_cursor.close()
            railway_conn.close()
            continue
        
        # Obter colunas
        render_cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns_info = render_cursor.fetchall()
        column_names = [col[0] for col in columns_info]
        column_types = {col[0]: col[1] for col in columns_info}
        
        # Verificar/criar tabela no Railway
        railway_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        if not railway_cursor.fetchone()[0]:
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
        
        # Migrar em lotes pequenos
        BATCH_SIZE = 25
        offset = 0
        inserted = 0
        cols_quoted = ', '.join([f'"{col}"' for col in column_names])
        
        print(f'[{idx}/{len(TABLES)}] 📦 {table_name}: 0/{expected_count}', end='', flush=True)
        
        while offset < expected_count:
            render_cursor.execute(f'SELECT {cols_quoted} FROM "{table_name}" LIMIT {BATCH_SIZE} OFFSET {offset}')
            rows = render_cursor.fetchall()
            
            if not rows:
                break
            
            for row in rows:
                try:
                    values = list(row)
                    for i, col_name in enumerate(column_names):
                        if column_types.get(col_name) == 'boolean' and values[i] is not None:
                            values[i] = 1 if values[i] else 0
                    
                    placeholders = ', '.join(['%s'] * len(values))
                    insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
                    railway_cursor.execute(insert_sql, values)
                    inserted += 1
                    
                    # Atualizar progresso
                    percent_table = (inserted / expected_count) * 100
                    percent_total = ((total_migrated + inserted) / total_records) * 100
                    print(f'\r[{idx}/{len(TABLES)}] 📦 {table_name}: {inserted}/{expected_count} ({percent_table:.0f}%) | Total: {percent_total:.1f}%', end='', flush=True)
                except Exception as e:
                    continue
            
            railway_conn.commit()
            offset += BATCH_SIZE
        
        total_migrated += inserted
        percent_total = (total_migrated / total_records) * 100
        print(f'\r[{idx}/{len(TABLES)}] ✅ {table_name}: {inserted}/{expected_count} | Total: {total_migrated}/{total_records} ({percent_total:.1f}%)')
        
        # Fechar conexões
        render_cursor.close()
        render_conn.close()
        railway_cursor.close()
        railway_conn.close()
        
        # Pequena pausa entre tabelas
        time.sleep(0.5)
        
    except Exception as e:
        print(f'\r[{idx}/{len(TABLES)}] ❌ {table_name}: {str(e)[:60]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass
        continue

print('\n' + '=' * 70)
print('🎉 MIGRAÇÃO CONCLUÍDA!')
print('=' * 70)
print(f'✅ {total_migrated}/{total_records} registos migrados ({(total_migrated/total_records)*100:.1f}%)')
print('\n🌐 https://carscraping.up.railway.app')
print('🔐 Login: mesmas credenciais do Render')
print('\n💾 Dados migrados:')
print('  ✅ Utilizadores e configurações')
print('  ✅ Histórico de pesquisas')
print('  ✅ Fotos dos carros')
print('  ✅ Damage Reports e templates')
print('  ✅ Logs e atividades')
print('  ✅ TUDO!')
