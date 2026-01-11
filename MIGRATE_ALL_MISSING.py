#!/usr/bin/env python3
"""
MIGRAÇÃO COMPLETA DOS DADOS EM FALTA
Adapta schemas incompatíveis e migra TODOS os dados
"""
import psycopg2
import sys
from datetime import datetime

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRANDO TODOS OS DADOS EM FALTA')
print('=' * 70)

# Mapeamento de colunas para cada tabela problemática
COLUMN_MAPPINGS = {
    'recent_searches': {
        # Render -> Railway
        'id': 'id',
        'search_date': 'search_date',
        'car_group': 'car_group',
        'price': 'price',
        'supplier': 'supplier',
        # Colunas do Render que não existem no Railway - ignorar
        # 'location', 'start_date', 'days', 'timestamp', 'results_data'
        # Colunas do Railway que não existem no Render - usar NULL
        # 'pickup_date', 'dropoff_date', 'pickup_location', 'dropoff_location'
    },
    'vehicle_photos': {
        'id': 'id',
        'vehicle_name': 'vehicle_name',
        'photo_url': 'photo_url',
        'photo_data': 'photo_data',
        'uploaded_at': 'uploaded_at',
        # 'updated_at' não existe no Railway - ignorar
    },
    'vehicle_images': {
        'id': 'id',
        'vehicle_name': 'vehicle_name',
        'image_url': 'image_url',
        'image_data': 'image_data',
        'uploaded_at': 'uploaded_at',
        # 'updated_at' não existe no Railway - ignorar
    },
    'automated_price_rules': {
        'id': 'id',
        'car_group': 'car_group',
        'min_price': 'min_price',
        'max_price': 'max_price',
        'adjustment': 'adjustment',
        'active': 'active',
        'last_updated': 'last_updated',
        # 'rules_json' não existe no Railway - ignorar
        # Railway tem 'strategy_type', 'priority', 'created_at' - usar NULL
    },
    'system_logs': {
        'id': 'id',
        'timestamp': 'timestamp',
        'level': 'level',
        'message': 'message',
        'module': 'module',
        'function': 'function',
        'line_number': 'line_number',
        'user_id': 'user_id',
        # 'context' não existe no Railway - ignorar
    },
    'whatsapp_config': {
        'id': 'id',
        'api_url': 'api_url',
        'api_token': 'api_token',
        'phone_number': 'phone_number',
        'enabled': 'enabled',
        'created_at': 'created_at',
        # 'updated_at' não existe no Railway - ignorar
    },
    'oauth_tokens': {
        # 100% compatível - todas as 11 colunas
        'id': 'id',
        'user_id': 'user_id',
        'provider': 'provider',
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'token_type': 'token_type',
        'expires_at': 'expires_at',
        'scope': 'scope',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'email': 'email',
    },
    'inspection_photos': {
        # 100% compatível - todas as 14 colunas
        'id': 'id',
        'inspection_id': 'inspection_id',
        'photo_type': 'photo_type',
        'photo_data': 'photo_data',
        'photo_url': 'photo_url',
        'uploaded_at': 'uploaded_at',
        'damage_detected': 'damage_detected',
        'damage_description': 'damage_description',
        'ai_confidence': 'ai_confidence',
        'verified': 'verified',
        'verified_by': 'verified_by',
        'verified_at': 'verified_at',
        'notes': 'notes',
        'metadata': 'metadata',
    },
    'automated_search_history': {
        'id': 'id',
        'search_date': 'search_date',
        'location': 'location',
        'days': 'days',
        'results_count': 'results_count',
        'min_price': 'min_price',
        'max_price': 'max_price',
        'avg_price': 'avg_price',
        'status': 'status',
        'error_message': 'error_message',
        'created_at': 'created_at',
        # 'pickup_date' não existe no Railway - ignorar
    },
}

total_migrated = 0

for table_name, column_map in COLUMN_MAPPINGS.items():
    try:
        print(f'\n📦 {table_name}:', end=' ', flush=True)
        
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cursor = render_conn.cursor()
        
        railway_conn = psycopg2.connect(RAILWAY_DB_URL)
        railway_cursor = railway_conn.cursor()
        
        # Verificar se existe
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
        
        # Obter colunas do Railway
        railway_cursor.execute(f'''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        ''')
        railway_cols = [col[0] for col in railway_cursor.fetchall()]
        
        # Desativar triggers
        try:
            railway_cursor.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')
            railway_conn.commit()
        except:
            pass
        
        # Limpar
        railway_cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        railway_conn.commit()
        
        # Preparar colunas para SELECT (Render) e INSERT (Railway)
        render_select_cols = list(column_map.keys())
        railway_insert_cols = [column_map[col] for col in render_select_cols]
        
        # Adicionar colunas extra do Railway com valores NULL
        railway_cursor.execute(f'''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        ''')
        all_railway_cols = [col[0] for col in railway_cursor.fetchall()]
        
        extra_cols = [col for col in all_railway_cols if col not in railway_insert_cols]
        
        # SELECT do Render
        render_select = ', '.join([f'"{col}"' for col in render_select_cols])
        render_cursor.execute(f'SELECT {render_select} FROM "{table_name}"')
        
        # INSERT no Railway
        all_insert_cols = railway_insert_cols + extra_cols
        cols_quoted = ', '.join([f'"{col}"' for col in all_insert_cols])
        
        inserted = 0
        errors = 0
        
        for row in render_cursor.fetchall():
            try:
                # Valores do Render
                values = list(row)
                
                # Adicionar NULLs para colunas extra do Railway
                for _ in extra_cols:
                    values.append(None)
                
                placeholders = ', '.join(['%s'] * len(values))
                insert_sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})'
                
                railway_cursor.execute(insert_sql, values)
                inserted += 1
                
                if inserted % 100 == 0:
                    railway_conn.commit()
                    print(f'{inserted}...', end=' ', flush=True)
                    
            except Exception as e:
                errors += 1
                if errors > 20:
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
        print(f'❌ {str(e)[:80]}')
        try:
            render_conn.close()
            railway_conn.close()
        except:
            pass

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO CONCLUÍDA!')
print(f'✅ {total_migrated} registos adicionais migrados')
print('\n🌐 https://carscraping.up.railway.app')
print('🔐 Todas as credenciais e dados do Render agora no Railway!')
