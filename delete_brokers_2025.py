import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== ELIMINAR DADOS DE BROKERS 2025 ===\n")
    
    # Verificar quantos existem
    cur.execute("""
        SELECT COUNT(*) 
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    total = cur.fetchone()[0]
    print(f"Total de registos de brokers em 2025: {total}")
    
    # Eliminar
    cur.execute("""
        DELETE FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    deleted = cur.rowcount
    conn.commit()
    
    print(f"✓ {deleted} registos eliminados\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
