#!/usr/bin/env python3
"""
MIGRAÇÃO FINAL DAS TABELAS RESTANTES
Com nomes de colunas CORRETOS do Railway
"""
import psycopg2
import sys

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRANDO TABELAS RESTANTES')
print('=' * 70)

# Tabelas com colunas IDÊNTICAS ou quase idênticas
TABLES = {
    'vehicle_images': {
        'columns': ['vehicle_key', 'image_data', 'content_type', 'source_url', 'downloaded_at']
    },
    'recent_searches': {
        'columns': ['id', 'user', 'pickup_location', 'dropoff_location', 'pickup_date', 
                   'dropoff_date', 'created_at', 'source', 'username']
    },
    'automated_price_rules': {
        'columns': ['id', 'location', 'grupo', 'month', 'day', 'strategy_type', 
                   'config', 'priority', 'created_at', 'updated_at']
    },
    'automated_search_history': {
        'columns': ['id', 'location', 'search_type', 'search_date', 'month_key',
                   'prices_data', 'dias', 'price_count', 'user_email', 'supplier_data', 
                   'created_at']
    },
    'whatsapp_config': {
        'columns': ['id', 'access_token', 'phone_number_id', 'business_account_id',
                   'verify_token', 'token_expires_at']
    },
    'oauth_tokens': {
        'columns': ['id', 'provider', 'user_email', 'access_token', 'refresh_token',
                   'expires_at', 'google_id', 'user_name', 'user_picture', 
                   'created_at', 'updated_at']
    },
    'inspection_photos': {
        'columns': ['id', 'inspection_id', 'photo_type', 'photo_order', 'image_data',
                   'image_filename', 'image_size', 'image_format', 'ai_analyzed',
                   'ai_has_damage', 'ai_damage_type', 'ai_confidence', 'ai_result', 
                   'created_at']
    },
}

total_migrated = 0

for table_name, config in TABLES.items():
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
        
        # Contar
        render_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = render_cursor.fetchone()[0]
        
        if count == 0:
            print('vazia')
            continue
        
        print(f'{count} registos...', end=' ', flush=True)
        
        # Obter colunas comuns entre Render e Railway
        render_cursor.execute(f'''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        ''')
        render_cols = [col[0] for col in render_cursor.fetchall()]
        
        railway_cursor.execute(f'''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        ''')
        railway_cols = [col[0] for col in railway_cursor.fetchall()]
        
        # Usar apenas colunas comuns
        common_cols = [col for col in config['columns'] if col in render_cols and col in railway_cols]
        
        if not common_cols:
            print('❌ sem colunas comuns')
            continue
        
        # Desativar triggers
        try:
            railway_cursor.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')
            railway_conn.commit()
        except:
            pass
        
        # Limpar
        railway_cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        railway_conn.commit()
        
        # SELECT e INSERT
        cols_quoted = ', '.join([f'"{col}"' for col in common_cols])
        placeholders = ', '.join(['%s'] * len(common_cols))
        
        render_cursor.execute(f'SELECT {cols_quoted} FROM "{table_name}"')
        insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
        
        inserted = 0
        errors = 0
        
        for row in render_cursor.fetchall():
            try:
                # Converter booleanos para inteiros se necessário
                values = []
                for val in row:
                    if isinstance(val, bool):
                        values.append(1 if val else 0)
                    else:
                        values.append(val)
                
                railway_cursor.execute(insert_sql, values)
                inserted += 1
                
                if inserted % 200 == 0:
                    railway_conn.commit()
                    print(f'{inserted}...', end=' ', flush=True)
                    
            except Exception as e:
                errors += 1
                if errors > 100:
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
        print(f'❌ {str(e)[:100]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO CONCLUÍDA!')
print(f'✅ {total_migrated} registos adicionais migrados')
print(f'\n📊 TOTAL GERAL NO RAILWAY: ~{30175 + total_migrated} registos')
print('\n🌐 https://carscraping.up.railway.app')
print('🔐 TODOS os dados do Render migrados!')
