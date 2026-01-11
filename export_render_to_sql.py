#!/usr/bin/env python3
"""
Exporta TODOS os dados do Render para ficheiro SQL
Depois podes importar manualmente no Railway quando tiver espaço
"""
import psycopg2
import sys

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
OUTPUT_FILE = '/tmp/render_backup.sql'

print('📥 EXPORTANDO DADOS DO RENDER PARA SQL')
print('=' * 70)

TABLES = [
    'users', 'app_settings', 'user_settings', 'activity_log',
    'automated_price_rules', 'automated_search_history',
    'price_automation_settings', 'recent_searches', 'system_logs',
    'whatsapp_config', 'whatsapp_contacts', 'whatsapp_conversations',
    'whatsapp_quick_replies', 'whatsapp_templates', 'oauth_tokens',
    'damage_reports', 'damage_report_templates', 'damage_report_coordinates',
    'damage_report_mapping_history', 'damage_report_numbering',
    'dr_email_templates', 'rental_agreement_templates',
    'rental_agreement_coordinates', 'rental_agreement_mapping_history',
    'vehicle_inspections', 'inspection_photos', 'vehicle_photos',
    'vehicle_images', 'vehicle_name_overrides', 'downloads_history',
]

try:
    conn = psycopg2.connect(RENDER_DB_URL)
    cursor = conn.cursor()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('-- BACKUP COMPLETO DO RENDER\n')
        f.write('-- Gerado automaticamente\n\n')
        
        total_rows = 0
        
        for table in TABLES:
            try:
                # Verificar se existe
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                if not cursor.fetchone()[0]:
                    continue
                
                # Contar registos
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                
                if count == 0:
                    continue
                
                print(f'📦 {table}: {count} registos...', end=' ', flush=True)
                
                # Obter estrutura
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                col_names = [col[0] for col in columns]
                col_types = {col[0]: col[1] for col in columns}
                
                # Criar tabela
                f.write(f'\n-- Tabela: {table}\n')
                f.write(f'DROP TABLE IF EXISTS "{table}" CASCADE;\n')
                
                col_defs = []
                for col_name, col_type in columns:
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
                    col_defs.append(f'  "{col_name}" {pg_type}')
                
                f.write(f'CREATE TABLE "{table}" (\n')
                f.write(',\n'.join(col_defs))
                f.write('\n);\n\n')
                
                # Exportar dados
                cols_quoted = ', '.join([f'"{col}"' for col in col_names])
                cursor.execute(f'SELECT {cols_quoted} FROM "{table}"')
                
                rows_written = 0
                for row in cursor.fetchall():
                    values = []
                    for i, val in enumerate(row):
                        col_name = col_names[i]
                        col_type = col_types[col_name]
                        
                        if val is None:
                            values.append('NULL')
                        elif 'boolean' in col_type:
                            values.append('1' if val else '0')
                        elif 'bytea' in col_type:
                            # Skip binary data
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            # Escapar strings
                            val_str = str(val).replace("'", "''")
                            values.append(f"'{val_str}'")
                    
                    f.write(f'INSERT INTO "{table}" ({cols_quoted}) VALUES ({", ".join(values)});\n')
                    rows_written += 1
                
                total_rows += rows_written
                print(f'✅ {rows_written}')
                
            except Exception as e:
                print(f'❌ {str(e)[:50]}')
                continue
        
        f.write(f'\n-- Total: {total_rows} registos exportados\n')
    
    cursor.close()
    conn.close()
    
    print('\n' + '=' * 70)
    print(f'✅ EXPORTAÇÃO CONCLUÍDA!')
    print(f'📄 Ficheiro: {OUTPUT_FILE}')
    print(f'📊 {total_rows} registos exportados')
    print('\nQuando o Railway tiver espaço, importa com:')
    print(f'  psql $RAILWAY_URL < {OUTPUT_FILE}')
    
except Exception as e:
    print(f'\n❌ Erro: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
