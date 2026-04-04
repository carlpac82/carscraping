import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Ver estrutura da tabela commission_bookings
    cur.execute("""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'commission_bookings'
        ORDER BY ordinal_position
    """)
    
    print("\n=== ESTRUTURA DA TABELA commission_bookings ===\n")
    print(f"{'Campo':<30} {'Tipo':<20} {'NULL?':<10} {'Default'}")
    print("-" * 80)
    
    for row in cur.fetchall():
        nullable = "SIM" if row[2] == 'YES' else "NÃO"
        default = row[3] if row[3] else ""
        print(f"{row[0]:<30} {row[1]:<20} {nullable:<10} {default}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
