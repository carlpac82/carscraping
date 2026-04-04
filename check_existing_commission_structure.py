import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== ESTRUTURA DE DADOS EXISTENTES EM COMMISSION_BOOKINGS ===\n")
    
    # Ver exemplos de 2024 (que devem estar corretos)
    cur.execute("""
        SELECT 
            voucher_number,
            client_name,
            pickup_date,
            price,
            commission_amount,
            commissioner_id,
            commission_rate
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2024
        ORDER BY pickup_date DESC
        LIMIT 20
    """)
    
    print("=== EXEMPLOS DE 2024 (dados corretos) ===\n")
    for row in cur.fetchall():
        print(f"Voucher: {row[0]}")
        print(f"Cliente: {row[1]}")
        print(f"Data: {row[2]}")
        print(f"Preço: €{row[3]:.2f}")
        print(f"Comissão: €{row[4]:.2f}")
        print(f"Commissioner ID: {row[5]}")
        print(f"Taxa: {row[6]}%")
        print("-" * 50)
    
    # Ver se há vouchers NULL
    cur.execute("""
        SELECT COUNT(*) 
        FROM commission_bookings
        WHERE voucher_number IS NULL OR voucher_number = ''
    """)
    null_vouchers = cur.fetchone()[0]
    print(f"\n=== VOUCHERS NULL/VAZIOS ===")
    print(f"Total de registos sem voucher: {null_vouchers}")
    
    # Ver exemplos sem voucher
    if null_vouchers > 0:
        cur.execute("""
            SELECT 
                id,
                client_name,
                pickup_date,
                price,
                commissioner_id
            FROM commission_bookings
            WHERE voucher_number IS NULL OR voucher_number = ''
            LIMIT 10
        """)
        print("\nExemplos de registos sem voucher:")
        for row in cur.fetchall():
            print(f"ID: {row[0]}, Cliente: {row[1]}, Data: {row[2]}, Preço: €{row[3]:.2f}, Comm ID: {row[4]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
