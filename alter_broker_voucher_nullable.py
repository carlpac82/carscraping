import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== ALTERANDO TABELA broker_bookings ===\n")
    print("Tornando voucher_number opcional (permite NULL)...")
    
    cur.execute("ALTER TABLE broker_bookings ALTER COLUMN voucher_number DROP NOT NULL")
    conn.commit()
    
    print("✓ Campo voucher_number agora permite NULL\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
