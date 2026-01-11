"""
Script para diagnosticar estrutura da tabela current_prices no Railway
"""
import os
import psycopg2
import json

# Conectar ao Railway
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PRIVATE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada")
    exit(1)

print(f"🔗 Conectando ao Railway...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 1. Verificar se tabela existe
print("\n📋 1. VERIFICAR SE TABELA EXISTE")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'current_prices'
    )
""")
exists = cur.fetchone()[0]
print(f"   Tabela existe: {exists}")

if not exists:
    print("❌ Tabela não existe! Precisa ser criada.")
    conn.close()
    exit(1)

# 2. Ver estrutura da tabela
print("\n📋 2. ESTRUTURA DA TABELA (colunas)")
cur.execute("""
    SELECT column_name, data_type, column_default, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'current_prices'
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
for col in columns:
    print(f"   {col[0]:20} {col[1]:20} default={col[2]} nullable={col[3]}")

# 3. Ver constraints
print("\n📋 3. CONSTRAINTS (UNIQUE, PRIMARY KEY, etc)")
cur.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'current_prices'::regclass
""")
constraints = cur.fetchall()
for name, type_code, definition in constraints:
    type_name = {'p': 'PRIMARY KEY', 'u': 'UNIQUE', 'f': 'FOREIGN KEY', 'c': 'CHECK'}.get(type_code, type_code)
    print(f"   {name:50} {type_name:15} {definition}")

# 4. Ver dados existentes
print("\n📋 4. DADOS EXISTENTES (primeiros 5 registos)")
cur.execute("""
    SELECT id, location, month, year, day_start, day_end, 
           LEFT(prices_data, 50) as prices_preview,
           updated_at
    FROM current_prices 
    ORDER BY id DESC
    LIMIT 5
""")
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"   ID={row[0]} {row[1]} {row[2]}/{row[3]} dias {row[4]}-{row[5]} prices={row[6]}... updated={row[7]}")
else:
    print("   (sem dados)")

# 5. Contar registos
print("\n📋 5. TOTAL DE REGISTOS")
cur.execute("SELECT COUNT(*) FROM current_prices")
total = cur.fetchone()[0]
print(f"   Total: {total} registos")

conn.close()
print("\n✅ Diagnóstico completo")
