#!/usr/bin/env python3
"""
Script para corrigir constraint da tabela current_prices no Railway PostgreSQL
Executa diretamente na base de dados para resolver o problema de cache
"""
import os
import psycopg2

# URL da base de dados Railway (do environment)
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_PRIVATE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada!")
    print("Execute: export DATABASE_URL='postgresql://...'")
    exit(1)

print(f"🔗 Conectando ao Railway PostgreSQL...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("✅ Conectado!")
    
    # 1. Verificar constraint atual
    print("\n📋 Verificando constraints atuais...")
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'current_prices'::regclass
          AND contype = 'u'
    """)
    
    constraints = cur.fetchall()
    print(f"Constraints encontradas: {len(constraints)}")
    for name, definition in constraints:
        print(f"  - {name}: {definition}")
    
    # 2. Remover constraint antiga se existir
    print("\n🗑️ Removendo constraints antigas...")
    for name, _ in constraints:
        print(f"  Removendo: {name}")
        cur.execute(f"ALTER TABLE current_prices DROP CONSTRAINT IF EXISTS {name}")
    
    # 3. Adicionar constraint correta
    print("\n➕ Adicionando constraint correta...")
    cur.execute("""
        ALTER TABLE current_prices 
        ADD CONSTRAINT current_prices_unique_period 
        UNIQUE (location, month, year, day_start, day_end)
    """)
    
    # 4. Verificar se colunas day_start e day_end existem
    print("\n📋 Verificando colunas...")
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'current_prices'
          AND column_name IN ('day_start', 'day_end')
    """)
    
    cols = [row[0] for row in cur.fetchall()]
    print(f"Colunas encontradas: {cols}")
    
    if 'day_start' not in cols:
        print("  ➕ Adicionando coluna day_start...")
        cur.execute("ALTER TABLE current_prices ADD COLUMN day_start INTEGER DEFAULT 1")
    
    if 'day_end' not in cols:
        print("  ➕ Adicionando coluna day_end...")
        cur.execute("ALTER TABLE current_prices ADD COLUMN day_end INTEGER DEFAULT 31")
    
    # 5. Atualizar registos existentes
    print("\n🔄 Atualizando registos existentes...")
    cur.execute("""
        UPDATE current_prices 
        SET day_start = 1, day_end = 31 
        WHERE day_start IS NULL OR day_end IS NULL
    """)
    updated = cur.rowcount
    print(f"  Atualizados: {updated} registos")
    
    # Commit
    conn.commit()
    
    print("\n✅ CONSTRAINT CORRIGIDA COM SUCESSO!")
    print("\n📋 Nova estrutura:")
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'current_prices'::regclass
          AND contype = 'u'
    """)
    
    for name, definition in cur.fetchall():
        print(f"  - {name}: {definition}")
    
    cur.close()
    conn.close()
    
    print("\n🎉 TUDO PRONTO! Agora o Railway pode guardar múltiplos períodos.")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
