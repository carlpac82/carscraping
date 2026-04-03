#!/usr/bin/env python3
"""
Verificar hotéis ignorados na base de dados
"""
import os
import psycopg2
from urllib.parse import urlparse

def check_missing_hotels():
    database_url = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break

    result = urlparse(database_url)
    conn = psycopg2.connect(
        database='railway',
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    cursor = conn.cursor()

    hotéis_procurar = ['BELA VISTA AVENIDA', 'INATEL PRAIA']

    print('🔍 Procurando hotéis ignorados na base de dados:')
    for hotel in hotéis_procurar:
        cursor.execute('SELECT id, name FROM commissioners WHERE UPPER(name) LIKE %s', (f'%{hotel}%',))
        results = cursor.fetchall()
        if results:
            print(f'✅ {hotel}:')
            for res in results:
                print(f'   ID: {res[0]} - {res[1]}')
        else:
            print(f'❌ {hotel}: Não encontrado')

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_missing_hotels()
