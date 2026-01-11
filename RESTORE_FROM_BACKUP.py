#!/usr/bin/env python3
"""
Restaura automated_price_rules e oauth_tokens do backup do Render para Railway
"""
import psycopg2
import os

BACKUP_DIR = '2026-01-09T20-39Z.dir'
RAILWAY_DB_URL = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'

print('🔄 RESTAURANDO DO BACKUP DO RENDER')
print('=' * 70)

# Conectar ao backup (é uma base de dados PostgreSQL)
backup_path = os.path.join(os.getcwd(), BACKUP_DIR)

if not os.path.exists(backup_path):
    print(f'❌ Backup não encontrado: {backup_path}')
    print('\nExecuta primeiro: tar -xf 2026-01-09T20-39Z.dir.tar')
    exit(1)

# Conectar ao Railway
railway_conn = psycopg2.connect(RAILWAY_DB_URL)
railway_cur = railway_conn.cursor()

# O backup é um dump em formato directory - vamos ler os ficheiros de dados
print(f'\n📂 Backup extraído em: {backup_path}')
print('\nProcurando ficheiros de dados...')

# Listar ficheiros no backup
for root, dirs, files in os.walk(backup_path):
    for file in files:
        if 'automated_price_rules' in file or 'oauth_tokens' in file:
            print(f'  Encontrado: {file}')

print('\n⚠️  NOTA: O backup está em formato PostgreSQL directory.')
print('Precisas de pg_restore para restaurar.')
print('\nInstala PostgreSQL:')
print('  brew install postgresql@14')
print('\nDepois executa:')
print('  PGPASSWORD="OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo" pg_restore \\')
print('    -h shortline.proxy.rlwy.net -p 45408 -U postgres -d railway \\')
print('    --data-only --table=automated_price_rules 2026-01-09T20-39Z.dir')

railway_cur.close()
railway_conn.close()
