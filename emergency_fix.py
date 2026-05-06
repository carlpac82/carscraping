#!/usr/bin/env python3
"""
EMERGENCY FIX - Matar TODAS as conexões e limpar
"""
import psycopg2
import time

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

print("🚨 EMERGENCY FIX - Killing all connections")
print("=" * 60)

try:
    # Conectar
    print("\n1️⃣ Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
    conn.autocommit = True
    cursor = conn.cursor()
    print("   ✅ Connected")
    
    # Ver estado atual
    print("\n2️⃣ Current connection state:")
    cursor.execute("""
        SELECT state, count(*) 
        FROM pg_stat_activity 
        WHERE datname = 'railway'
        GROUP BY state;
    """)
    for state, count in cursor.fetchall():
        print(f"   {state or 'unknown'}: {count}")
    
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = 'railway';")
    total_before = cursor.fetchone()[0]
    print(f"   TOTAL: {total_before} connections")
    
    # MATAR TODAS as conexões (exceto a nossa)
    print("\n3️⃣ Killing ALL connections (except this one)...")
    cursor.execute("""
        SELECT pg_terminate_backend(pid), pid, state
        FROM pg_stat_activity 
        WHERE datname = 'railway'
        AND pid != pg_backend_pid();
    """)
    
    killed = cursor.fetchall()
    print(f"   ✅ Killed {len(killed)} connections")
    
    # Aguardar 2 segundos
    print("\n4️⃣ Waiting 2 seconds...")
    time.sleep(2)
    
    # Verificar estado final
    print("\n5️⃣ Final state:")
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = 'railway';")
    total_after = cursor.fetchone()[0]
    print(f"   TOTAL: {total_after} connections")
    print(f"   FREED: {total_before - total_after} connections")
    
    # Adicionar coluna em falta
    print("\n6️⃣ Adding missing column...")
    try:
        cursor.execute("ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS return_location TEXT;")
        print("   ✅ Column added")
    except Exception as e:
        print(f"   ℹ️  {e}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ EMERGENCY FIX COMPLETED!")
    print("=" * 60)
    print("\n🔄 Railway should auto-restart the application now.")
    print("⏳ Wait 1-2 minutes and check: https://rentalprices.pt")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
