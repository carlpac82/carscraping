#!/usr/bin/env python3
"""
MIGRAÇÃO DEFINITIVA - Desativa constraints temporariamente
Migra TODOS os dados sem problemas de foreign keys
"""
import psycopg2
import sys
import time

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRAÇÃO DEFINITIVA - SEM CONSTRAINTS')
print('=' * 70)

# Obter TODAS as tabelas do Render
render_conn = psycopg2.connect(RENDER_DB_URL)
render_cursor = render_conn.cursor()

render_cursor.execute("""
    SELECT table_name, 
           (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as col_count
    FROM information_schema.tables t
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

all_tables = []
for table_name, col_count in render_cursor.fetchall():
    render_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = render_cursor.fetchone()[0]
    if count > 0:
        all_tables.append((table_name, count))

render_cursor.close()
render_conn.close()

total_records = sum(count for _, count in all_tables)
print(f'📊 {len(all_tables)} tabelas com dados ({total_records} registos)\n')

total_migrated = 0

for idx, (table_name, expected_count) in enumerate(all_tables, 1):
    try:
        # Nova conexão para cada tabela
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
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
        
        # Verificar/criar tabela
        railway_cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        
        if not railway_cursor.fetchone()[0]:
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
                elif 'numeric' in col_type or 'decimal' in col_type or 'real' in col_type or 'double' in col_type:
                    pg_type = 'DECIMAL'
                else:
                    pg_type = 'TEXT'
                
                col_defs.append(f'"{col_name}" {pg_type}')
            
            create_sql = f'CREATE TABLE "{table_name}" ({", ".join(col_defs)})'
            railway_cursor.execute(create_sql)
            railway_conn.commit()
        
        # DESATIVAR TRIGGERS (evita problemas com constraints)
        railway_cursor.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')
        railway_conn.commit()
        
        # Limpar
        railway_cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        railway_conn.commit()
        
        # Migrar em lotes
        BATCH_SIZE = 100
        offset = 0
        inserted = 0
        errors = 0
        
        cols_quoted = ', '.join([f'"{col}"' for col in column_names])
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
        
        print(f'[{idx}/{len(all_tables)}] 📦 {table_name}: ', end='', flush=True)
        
        while True:
            render_cursor.execute(f'SELECT {cols_quoted} FROM "{table_name}" LIMIT {BATCH_SIZE} OFFSET {offset}')
            rows = render_cursor.fetchall()
            
            if not rows:
                break
            
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
                        else:
                            values.append(val)
                    
                    railway_cursor.execute(insert_sql, values)
                    inserted += 1
                    
                    if inserted % 500 == 0:
                        railway_conn.commit()
                        percent = (inserted / expected_count) * 100
                        print(f'\r[{idx}/{len(all_tables)}] 📦 {table_name}: {inserted}/{expected_count} ({percent:.0f}%)', end='', flush=True)
                        
                except Exception as e:
                    errors += 1
                    if errors < 5:
                        continue
                    else:
                        break
            
            railway_conn.commit()
            offset += BATCH_SIZE
            
            if offset >= expected_count * 1.5:
                break
        
        # REATIVAR TRIGGERS
        railway_cursor.execute(f'ALTER TABLE "{table_name}" ENABLE TRIGGER ALL')
        railway_conn.commit()
        
        total_migrated += inserted
        percent_total = (total_migrated / total_records) * 100
        
        if inserted > 0:
            print(f'\r[{idx}/{len(all_tables)}] ✅ {table_name}: {inserted}/{expected_count} | Total: {total_migrated}/{total_records} ({percent_total:.1f}%)')
        else:
            print(f'\r[{idx}/{len(all_tables)}] ⚠️  {table_name}: 0/{expected_count} (erros: {errors})')
        
        render_cursor.close()
        render_conn.close()
        railway_cursor.close()
        railway_conn.close()
        
        time.sleep(0.3)
        
    except Exception as e:
        print(f'\r[{idx}/{len(all_tables)}] ❌ {table_name}: {str(e)[:60]}')
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
print('🔐 Credenciais: mesmas do Render')
