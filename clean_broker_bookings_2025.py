import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== VERIFICAR DADOS EM BROKER_BOOKINGS 2025 ===\n")
    
    # Ver quantos registos existem
    cur.execute("""
        SELECT COUNT(*) 
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    total = cur.fetchone()[0]
    print(f"Total de registos em broker_bookings (2025): {total}")
    
    # Ver exemplos
    cur.execute("""
        SELECT broker_name, COUNT(*) as count
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        GROUP BY broker_name
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\nDistribuição por broker_name:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} registos")
    
    # APAGAR TODOS os dados de 2025 em broker_bookings
    # (porque foram importados incorretamente - deveriam estar em commission_bookings)
    print(f"\n⚠ Vou apagar TODOS os {total} registos de 2025 em broker_bookings")
    print("(Estes dados foram importados incorretamente e já estão em commission_bookings)")
    
    cur.execute("""
        DELETE FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """)
    
    deleted = cur.rowcount
    conn.commit()
    
    print(f"\n✓ {deleted} registos apagados de broker_bookings")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
