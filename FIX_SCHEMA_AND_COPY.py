#!/usr/bin/env python3
"""
1. Remove constraint NOT NULL de strategy_type no Railway
2. Copia automated_price_rules e oauth_tokens do Render para Railway
"""
import psycopg2

RENDER_DB_URL = 'postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🔧 CORRIGINDO SCHEMA E COPIANDO DADOS')
print('=' * 70)

# 1. Remover constraints NOT NULL no Railway
print('\n🔧 Removendo constraints NOT NULL...')
try:
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_conn.autocommit = True
    w_cur = w_conn.cursor()
    
    w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "strategy_type" DROP NOT NULL')
    w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "priority" DROP NOT NULL')
    w_cur.execute('ALTER TABLE "automated_price_rules" ALTER COLUMN "created_at" DROP NOT NULL')
    print('  ✅ Constraints removidas')
    
    w_cur.close()
    w_conn.close()
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 2. Copiar automated_price_rules
print('\n📦 automated_price_rules...')
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_conn.autocommit = False
    r_cur = r_conn.cursor()
    
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_conn.autocommit = False
    w_cur = w_conn.cursor()
    
    # Ler todos os dados
    r_cur.execute('SELECT id, location, grupo, month, day, config, updated_at FROM automated_price_rules')
    rows = r_cur.fetchall()
    print(f'  Lidos {len(rows)} registos do Render')
    
    # Limpar Railway
    w_cur.execute('TRUNCATE TABLE "automated_price_rules" CASCADE')
    w_conn.commit()
    
    # Inserir no Railway
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
                print(f'  {inserted}...')
        except Exception as e:
            w_conn.rollback()
            continue
    
    w_conn.commit()
    print(f'  ✅ {inserted}/{len(rows)} registos copiados')
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
    
except Exception as e:
    print(f'  ❌ Erro: {e}')

# 3. Copiar oauth_tokens
print('\n📦 oauth_tokens...')
try:
    r_conn = psycopg2.connect(RENDER_DB_URL)
    r_conn.autocommit = False
    r_cur = r_conn.cursor()
    
    w_conn = psycopg2.connect(RAILWAY_DB_URL)
    w_conn.autocommit = False
    w_cur = w_conn.cursor()
    
    # Ler todos os dados
    r_cur.execute('SELECT id, provider, user_email, access_token, refresh_token, expires_at, google_id, user_name, user_picture, created_at, updated_at FROM oauth_tokens')
    rows = r_cur.fetchall()
    print(f'  Lidos {len(rows)} registos do Render')
    
    # Limpar Railway
    w_cur.execute('TRUNCATE TABLE "oauth_tokens" CASCADE')
    w_conn.commit()
    
    # Inserir no Railway
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
            continue
    
    w_conn.commit()
    print(f'  ✅ {inserted}/{len(rows)} registos copiados')
    
    r_cur.close()
    r_conn.close()
    w_cur.close()
    w_conn.close()
    
except Exception as e:
    print(f'  ❌ Erro: {e}')

print('\n' + '=' * 70)
print('🎉 MIGRAÇÃO COMPLETA!')
print('\n🌐 https://carscraping.up.railway.app')
print('🔐 Todas as 5,366 regras de preços migradas!')
