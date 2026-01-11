#!/usr/bin/env python3
"""
Migra as últimas 3 tabelas em falta
"""
import psycopg2

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRANDO ÚLTIMAS 3 TABELAS')
print('=' * 70)

total = 0

# 1. recent_searches (1,903 registos)
print('\n📦 recent_searches (1,903 registos)...', end=' ', flush=True)
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_cur = r_conn.cursor()
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    w_cur.execute('TRUNCATE TABLE "recent_searches" CASCADE')
    w_conn.commit()
    
    # Render: id, location, start_date, days, results_data, timestamp, user, created_at, source, username
    # Railway: id, user, pickup_location, dropoff_location, pickup_date, dropoff_date, created_at, source, username
    r_cur.execute('SELECT id, location, start_date, "user", created_at, source, username FROM recent_searches')
    
    inserted = 0
    for row in r_cur.fetchall():
        try:
            w_cur.execute('''
                INSERT INTO "recent_searches" ("id", "pickup_location", "pickup_date", "user", "created_at", "source", "username")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', row)
            inserted += 1
            if inserted % 500 == 0:
                w_conn.commit()
                print(f'{inserted}...', end=' ', flush=True)
        except:
            pass
    
    w_conn.commit()
    print(f'✅ {inserted}')
    total += inserted
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
except Exception as e:
    print(f'❌ {e}')

# 2. automated_price_rules (5,363 registos)
print('\n📦 automated_price_rules (5,363 registos)...', end=' ', flush=True)
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_cur = r_conn.cursor()
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    w_cur.execute('TRUNCATE TABLE "automated_price_rules" CASCADE')
    w_conn.commit()
    
    # Render: id, location, grupo, month, day, rules_json, updated_at, config
    # Railway: id, location, grupo, month, day, strategy_type, config, priority, created_at, updated_at
    r_cur.execute('SELECT id, location, grupo, "month", "day", config, updated_at FROM automated_price_rules')
    
    inserted = 0
    for row in r_cur.fetchall():
        try:
            w_cur.execute('''
                INSERT INTO "automated_price_rules" ("id", "location", "grupo", "month", "day", "config", "updated_at")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', row)
            inserted += 1
            if inserted % 1000 == 0:
                w_conn.commit()
                print(f'{inserted}...', end=' ', flush=True)
        except:
            pass
    
    w_conn.commit()
    print(f'✅ {inserted}')
    total += inserted
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
except Exception as e:
    print(f'❌ {e}')

# 3. oauth_tokens (3 registos)
print('\n📦 oauth_tokens (3 registos)...', end=' ', flush=True)
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_cur = r_conn.cursor()
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    w_cur.execute('TRUNCATE TABLE "oauth_tokens" CASCADE')
    w_conn.commit()
    
    r_cur.execute('SELECT id, provider, user_email, access_token, refresh_token, expires_at, google_id, user_name, user_picture, created_at, updated_at FROM oauth_tokens')
    
    inserted = 0
    for row in r_cur.fetchall():
        try:
            w_cur.execute('''
                INSERT INTO "oauth_tokens" ("id", "provider", "user_email", "access_token", "refresh_token", "expires_at", "google_id", "user_name", "user_picture", "created_at", "updated_at")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', row)
            inserted += 1
        except:
            pass
    
    w_conn.commit()
    print(f'✅ {inserted}')
    total += inserted
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
except Exception as e:
    print(f'❌ {e}')

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO CONCLUÍDA!')
print(f'✅ {total} registos adicionais migrados')
print(f'\n📊 TOTAL FINAL: {30552 + total:,} registos no Railway')
print('\n🌐 https://carscraping.up.railway.app')
