#!/usr/bin/env python3
import os
import sys

print("🔍 DIAGNÓSTICO DE CONEXÃO DATABASE")
print("=" * 50)

# Verificar DATABASE_URL
database_url = os.getenv("DATABASE_URL")
print(f"\n1. DATABASE_URL definida: {database_url is not None}")
if database_url:
    # Mostrar apenas início e fim (segurança)
    safe_url = database_url[:20] + "..." + database_url[-20:] if len(database_url) > 40 else database_url
    print(f"   URL: {safe_url}")
else:
    print("   ❌ DATABASE_URL não encontrada!")

# Tentar importar database.py
print("\n2. Importando database.py...")
try:
    from database import USE_POSTGRES, _db_connect
    print(f"   ✅ Importado com sucesso")
    print(f"   USE_POSTGRES: {USE_POSTGRES}")
except Exception as e:
    print(f"   ❌ Erro ao importar: {e}")
    sys.exit(1)

# Tentar conectar
print("\n3. Testando conexão...")
try:
    conn = _db_connect()
    print(f"   ✅ Conexão estabelecida")
    print(f"   Tipo: {type(conn)}")
    print(f"   Módulo: {conn.__class__.__module__}")
    
    # Verificar se é PostgreSQL
    is_postgres = conn.__class__.__module__ == 'psycopg2.extensions'
    print(f"   É PostgreSQL: {is_postgres}")
    
    if is_postgres:
        print("\n✅ TUDO OK - Usando PostgreSQL!")
    else:
        print("\n❌ PROBLEMA - Usando SQLite em vez de PostgreSQL!")
        
except Exception as e:
    print(f"   ❌ Erro na conexão: {e}")
    import traceback
    traceback.print_exc()
