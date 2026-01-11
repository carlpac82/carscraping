#!/usr/bin/env python3
"""
Migra as últimas 4 tabelas em falta do Render para Railway:
- recent_searches (1,903 registos)
- automated_search_history (83 registos em falta)
- inspection_photos (30 registos)
- vehicle_inspections (8 registos)
"""
import psycopg2

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRANDO ÚLTIMAS 4 TABELAS')
print('=' * 70)

def migrate_table(table_name, render_cursor, railway_conn):
    """Migra uma tabela do Render para Railway"""
    w_cur = railway_conn.cursor()
    
    # Obter colunas do Render
    render_cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    render_cols = [c[0] for c in render_cursor.fetchall()]
    
    # Obter colunas do Railway
    w_cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    railway_cols = [c[0] for c in w_cur.fetchall()]
    
    # Colunas comuns
    common_cols = [c for c in render_cols if c in railway_cols]
    
    print(f'\n📦 {table_name}...')
    print(f'  Colunas comuns: {len(common_cols)}/{len(render_cols)}')
    
    # Ler dados do Render
    cols_str = ', '.join([f'"{c}"' for c in common_cols])
    render_cursor.execute(f'SELECT {cols_str} FROM "{table_name}"')
    rows = render_cursor.fetchall()
    print(f'  Lidos {len(rows)} registos do Render')
    
    if len(rows) == 0:
        print(f'  ⚠️  Nenhum registo para migrar')
        w_cur.close()
        return 0
    
    # Limpar Railway
    w_cur.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
    railway_conn.commit()
    
    # Inserir no Railway
    placeholders = ', '.join(['%s'] * len(common_cols))
    insert_sql = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'
    
    inserted = 0
    for row in rows:
        try:
            w_cur.execute(insert_sql, row)
            inserted += 1
            if inserted % 500 == 0:
                railway_conn.commit()
                print(f'  {inserted}...')
        except Exception as e:
            print(f'  ❌ Erro no registo {inserted + 1}: {e}')
            railway_conn.rollback()
            continue
    
    railway_conn.commit()
    print(f'  ✅ {inserted}/{len(rows)} registos copiados')
    
    w_cur.close()
    return inserted

# Conectar
r_conn = psycopg2.connect(RENDER_DB_URL)
r_conn.autocommit = False
r_cur = r_conn.cursor()

w_conn = psycopg2.connect(RAILWAY_DB_URL)
w_conn.autocommit = False

total_migrated = 0

# 1. recent_searches
try:
    total_migrated += migrate_table('recent_searches', r_cur, w_conn)
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 2. automated_search_history
try:
    total_migrated += migrate_table('automated_search_history', r_cur, w_conn)
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 3. inspection_photos
try:
    total_migrated += migrate_table('inspection_photos', r_cur, w_conn)
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 4. vehicle_inspections
try:
    total_migrated += migrate_table('vehicle_inspections', r_cur, w_conn)
except Exception as e:
    print(f'  ❌ Erro: {e}')

r_cur.close()
r_conn.close()
w_conn.close()

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO CONCLUÍDA!')
print(f'📊 Total migrado: {total_migrated:,} registos')
print('\n🌐 https://carscraping.up.railway.app')
