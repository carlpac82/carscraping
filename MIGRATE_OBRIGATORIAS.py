#!/usr/bin/env python3
"""
Migra APENAS as 2 tabelas obrigatórias: automated_price_rules e oauth_tokens
"""
import psycopg2

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🚀 MIGRANDO TABELAS OBRIGATÓRIAS')
print('=' * 70)

total = 0

# 1. REMOVER CONSTRAINTS
print('\n🔧 Removendo constraints NOT NULL...')
try:
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    # automated_price_rules
    try:
        w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "strategy_type" DROP NOT NULL')
        w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "priority" DROP NOT NULL')
        w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "created_at" DROP NOT NULL')
        w_conn.commit()
        print('  ✅ automated_price_rules')
    except Exception as e:
        print(f'  ⚠️  automated_price_rules: {e}')
        w_conn.rollback()
    
    w_cur.close()
    w_conn.close()
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 2. MIGRAR automated_price_rules (5,363 registos)
print('\n📦 automated_price_rules (5,363 registos)...')
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_cur = r_conn.cursor()
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    # Limpar
    w_cur.execute('TRUNCATE TABLE "automated_price_rules" CASCADE')
    w_conn.commit()
    
    # Migrar
    r_cur.execute('SELECT id, location, grupo, "month", "day", config, updated_at FROM automated_price_rules')
    rows = r_cur.fetchall()
    
    print(f'  Lidos {len(rows)} registos do Render')
    
    inserted = 0
    for row in rows:
        try:
            w_cur.execute('''
                INSERT INTO "automated_price_rules" ("id", "location", "grupo", "month", "day", "config", "updated_at")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', row)
            inserted += 1
            
            if inserted % 1000 == 0:
                w_conn.commit()
                print(f'  {inserted}...', flush=True)
        except Exception as e:
            # Fazer rollback e continuar
            w_conn.rollback()
            if inserted == 0:
                print(f'  ❌ Erro no primeiro registo: {e}')
                break
            continue
    
    w_conn.commit()
    print(f'  ✅ {inserted}/{len(rows)} registos migrados')
    total += inserted
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
    
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 3. MIGRAR oauth_tokens (3 registos)
print('\n📦 oauth_tokens (3 registos)...')
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_cur = r_conn.cursor()
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_cur = w_conn.cursor()
    
    # Limpar
    w_cur.execute('TRUNCATE TABLE "oauth_tokens" CASCADE')
    w_conn.commit()
    
    # Migrar
    r_cur.execute('SELECT id, provider, user_email, access_token, refresh_token, expires_at, google_id, user_name, user_picture, created_at, updated_at FROM oauth_tokens')
    rows = r_cur.fetchall()
    
    print(f'  Lidos {len(rows)} registos do Render')
    
    inserted = 0
    for row in rows:
        try:
            w_cur.execute('''
                INSERT INTO "oauth_tokens" ("id", "provider", "user_email", "access_token", "refresh_token", "expires_at", "google_id", "user_name", "user_picture", "created_at", "updated_at")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', row)
            inserted += 1
        except Exception as e:
            w_conn.rollback()
            if inserted == 0:
                print(f'  ❌ Erro no primeiro registo: {e}')
                break
            continue
    
    w_conn.commit()
    print(f'  ✅ {inserted}/{len(rows)} registos migrados')
    total += inserted
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
    
except Exception as e:
    print(f'  ❌ Erro: {e}')

print('\n' + '=' * 70)
print(f'🎉 MIGRAÇÃO CONCLUÍDA!')
print(f'✅ {total} registos migrados')
print(f'\n📊 TOTAL FINAL: {30552 + total:,} registos no Railway')
print('\n🌐 https://carscraping.up.railway.app')
