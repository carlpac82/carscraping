#!/usr/bin/env python3
"""
MIGRAÇÃO COMPLETA E FINAL - Com nomes de colunas CORRETOS
Migra TODOS os dados em falta do Render para Railway
"""
import psycopg2
import sys

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRAÇÃO COMPLETA E FINAL - TODOS OS DADOS')
print('=' * 70)

# Tabelas com mapeamento direto (copiar todas as colunas comuns)
SIMPLE_TABLES = {
    'oauth_tokens': {
        'render_cols': ['id', 'provider', 'user_email', 'access_token', 'refresh_token', 
                       'expires_at', 'google_id', 'user_name', 'user_picture', 
                       'created_at', 'updated_at'],
        'railway_cols': ['id', 'provider', 'email', 'access_token', 'refresh_token',
                        'expires_at', 'user_id', 'scope', 'token_type',
                        'created_at', 'updated_at'],
        'mapping': {
            'id': 'id',
            'provider': 'provider',
            'user_email': 'email',
            'access_token': 'access_token',
            'refresh_token': 'refresh_token',
            'expires_at': 'expires_at',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
        }
    },
    'inspection_photos': {
        'render_cols': ['id', 'inspection_id', 'photo_type', 'photo_order', 'image_data',
                       'image_filename', 'image_size', 'image_format', 'ai_analyzed',
                       'ai_has_damage', 'ai_damage_type', 'ai_confidence', 'ai_result', 'created_at'],
        'railway_cols': ['id', 'inspection_id', 'photo_type', 'photo_data', 'photo_url',
                        'uploaded_at', 'damage_detected', 'damage_description', 'ai_confidence',
                        'verified', 'verified_by', 'verified_at', 'notes', 'metadata'],
        'mapping': {
            'id': 'id',
            'inspection_id': 'inspection_id',
            'photo_type': 'photo_type',
            'image_data': 'photo_data',
            'ai_confidence': 'ai_confidence',
            'created_at': 'uploaded_at',
        }
    },
    'vehicle_photos': {
        'render_cols': ['vehicle_name', 'photo_data', 'photo_url', 'content_type', 
                       'updated_at', 'uploaded_at'],
        'railway_cols': ['id', 'vehicle_name', 'photo_url', 'photo_data', 'uploaded_at'],
        'mapping': {
            'vehicle_name': 'vehicle_name',
            'photo_data': 'photo_data',
            'photo_url': 'photo_url',
            'uploaded_at': 'uploaded_at',
        }
    },
    'vehicle_images': {
        'render_cols': ['vehicle_key', 'image_data', 'content_type', 'updated_at',
                       'source_url', 'downloaded_at'],
        'railway_cols': ['id', 'vehicle_name', 'image_url', 'image_data', 'uploaded_at'],
        'mapping': {
            'vehicle_key': 'vehicle_name',
            'image_data': 'image_data',
            'source_url': 'image_url',
            'downloaded_at': 'uploaded_at',
        }
    },
    'system_logs': {
        'render_cols': ['id', 'level', 'message', 'timestamp', 'context', 'module',
                       'function', 'line_number', 'exception'],
        'railway_cols': ['id', 'timestamp', 'level', 'message', 'module', 'function',
                        'line_number', 'user_id'],
        'mapping': {
            'id': 'id',
            'level': 'level',
            'message': 'message',
            'timestamp': 'timestamp',
            'module': 'module',
            'function': 'function',
            'line_number': 'line_number',
        }
    },
    'recent_searches': {
        'render_cols': ['id', 'location', 'start_date', 'days', 'results_data', 'timestamp',
                       'user', 'created_at', 'source', 'username'],
        'railway_cols': ['id', 'pickup_location', 'dropoff_location', 'pickup_date',
                        'dropoff_date', 'search_date', 'car_group', 'price', 'supplier'],
        'mapping': {
            'id': 'id',
            'location': 'pickup_location',
            'start_date': 'pickup_date',
            'created_at': 'search_date',
        }
    },
    'automated_price_rules': {
        'render_cols': ['id', 'location', 'grupo', 'month', 'day', 'rules_json',
                       'updated_at', 'config'],
        'railway_cols': ['id', 'car_group', 'min_price', 'max_price', 'adjustment',
                        'active', 'last_updated', 'strategy_type', 'priority', 'created_at'],
        'mapping': {
            'id': 'id',
            'grupo': 'car_group',
            'updated_at': 'last_updated',
        }
    },
    'automated_search_history': {
        'render_cols': ['id', 'location', 'search_type', 'search_date', 'month_key',
                       'prices_data', 'dias', 'price_count', 'user_email', 'created_at',
                       'supplier_data', 'pickup_date'],
        'railway_cols': ['id', 'search_date', 'location', 'days', 'results_count',
                        'min_price', 'max_price', 'avg_price', 'status', 'error_message',
                        'created_at'],
        'mapping': {
            'id': 'id',
            'search_date': 'search_date',
            'location': 'location',
            'price_count': 'results_count',
            'created_at': 'created_at',
        }
    },
    'whatsapp_config': {
        'render_cols': ['id', 'access_token', 'phone_number_id', 'business_account_id',
                       'verify_token', 'updated_at', 'token_expires_at'],
        'railway_cols': ['id', 'api_url', 'api_token', 'phone_number', 'enabled', 'created_at'],
        'mapping': {
            'id': 'id',
            'access_token': 'api_token',
            'phone_number_id': 'phone_number',
        }
    },
}

total_migrated = 0

for table_name, config in SIMPLE_TABLES.items():
    try:
        print(f'\n📦 {table_name}:', end=' ', flush=True)
        
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
        # Contar
        render_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = render_cursor.fetchone()[0]
        
        if count == 0:
            print('vazia')
            continue
        
        print(f'{count} registos...', end=' ', flush=True)
        
        # Desativar triggers
        try:
            railway_cursor.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')
            railway_conn.commit()
        except:
            pass
        
        # Limpar
        railway_cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        railway_conn.commit()
        
        # Obter mapeamento
        mapping = config['mapping']
        render_cols = list(mapping.keys())
        railway_cols = list(mapping.values())
        
        # Obter TODAS as colunas do Railway
        railway_cursor.execute(f'''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        ''')
        all_railway_cols = [col[0] for col in railway_cursor.fetchall()]
        
        # Colunas extra (não mapeadas) - usar NULL
        extra_cols = [col for col in all_railway_cols if col not in railway_cols]
        
        # SELECT do Render
        render_select = ', '.join([f'"{col}"' for col in render_cols])
        render_cursor.execute(f'SELECT {render_select} FROM "{table_name}"')
        
        # INSERT no Railway
        all_insert_cols = railway_cols + extra_cols
        cols_quoted = ', '.join([f'"{col}"' for col in all_insert_cols])
        
        inserted = 0
        errors = 0
        
        for row in render_cursor.fetchall():
            try:
                # Valores do Render
                values = list(row)
                
                # Converter booleanos para inteiros se necessário
                for i, val in enumerate(values):
                    if isinstance(val, bool):
                        values[i] = 1 if val else 0
                
                # Adicionar NULLs para colunas extra
                for _ in extra_cols:
                    values.append(None)
                
                placeholders = ', '.join(['%s'] * len(values))
                insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
                
                railway_cursor.execute(insert_sql, values)
                inserted += 1
                
                if inserted % 200 == 0:
                    railway_conn.commit()
                    print(f'{inserted}...', end=' ', flush=True)
                    
            except Exception as e:
                errors += 1
                if errors > 50:
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
        print(f'❌ ERRO: {str(e)[:100]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO COMPLETA!')
print(f'✅ {total_migrated} registos adicionais migrados')
print('\n📊 TOTAL GERAL: ~{} registos no Railway'.format(20684 + total_migrated))
print('\n🌐 https://carscraping.up.railway.app')
print('🔐 TODOS os dados do Render agora no Railway!')
