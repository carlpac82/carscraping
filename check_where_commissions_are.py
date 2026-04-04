import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== VERIFICAR ONDE ESTÃO OS DADOS DE COMISSIONISTAS 2025 ===\n")
    
    # Check broker_bookings
    cur.execute("""
        SELECT COUNT(*) 
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    broker_count = cur.fetchone()[0]
    print(f"Registos em broker_bookings (2025): {broker_count}")
    
    # Check commission_bookings
    cur.execute("""
        SELECT COUNT(*) 
        FROM commission_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    commission_count = cur.fetchone()[0]
    print(f"Registos em commission_bookings (2025): {commission_count}")
    
    # Check commissioners table
    print("\n=== COMISSIONISTAS NA BASE DE DADOS ===\n")
    cur.execute("""
        SELECT id, name, email, commission_rate
        FROM commissioners
        ORDER BY name
    """)
    
    commissioners = cur.fetchall()
    print(f"Total de comissionistas: {len(commissioners)}\n")
    for comm in commissioners:
        print(f"ID: {comm[0]}, Nome: {comm[1]}, Email: {comm[2]}, Taxa: {comm[3]}%")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
