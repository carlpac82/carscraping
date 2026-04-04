import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def check_brokers_vs_commissioners():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("1. VERIFICAR BROKERS NA TABELA COMMISSIONERS")
    print("=" * 80)
    
    # Brokers conhecidos que NÃO devem estar em commissioners
    broker_names = [
        'DISCOVERCARS-PREPAID',
        'CARALLIANCE-POA',
        'CARALLIANCE-PREPAID',
        'RENTALCARS',
        'BROKERS - DIRECTOS'
    ]
    
    query = "SELECT id, name FROM commissioners WHERE name = ANY(%s)"
    cur.execute(query, (broker_names,))
    wrong_commissioners = cur.fetchall()
    
    if wrong_commissioners:
        print(f"\n⚠️  ENCONTRADOS {len(wrong_commissioners)} BROKERS INCORRETAMENTE EM COMMISSIONERS:")
        for comm_id, name in wrong_commissioners:
            # Verificar quantas reservas têm
            cur.execute("SELECT COUNT(*) FROM commission_bookings WHERE commissioner_id = %s", (comm_id,))
            count = cur.fetchone()[0]
            print(f"  ID {comm_id}: {name} ({count} reservas)")
    else:
        print("\n✓ Nenhum broker conhecido encontrado em commissioners")
    
    # Verificar todos os comissionistas com keywords de broker
    print("\n" + "=" * 80)
    print("PROCURAR OUTROS POSSÍVEIS BROKERS:")
    print("=" * 80)
    
    keywords = ['PREPAID', 'POA', 'DISCOVER', 'CARALLIANCE', 'RENTAL']
    
    for keyword in keywords:
        query = "SELECT id, name FROM commissioners WHERE UPPER(name) LIKE %s"
        cur.execute(query, (f'%{keyword}%',))
        results = cur.fetchall()
        
        if results:
            print(f"\n'{keyword}' encontrado em:")
            for comm_id, name in results:
                cur.execute("SELECT COUNT(*) FROM commission_bookings WHERE commissioner_id = %s", (comm_id,))
                count = cur.fetchone()[0]
                print(f"  ID {comm_id}: {name} ({count} reservas)")
    
    # Verificar brokers na tabela broker_bookings
    print("\n" + "=" * 80)
    print("2. VERIFICAR CAMPOS DOS BROKERS (broker_bookings)")
    print("=" * 80)
    
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN voucher_number IS NULL OR voucher_number = '' THEN 1 END) as sem_voucher,
            COUNT(CASE WHEN total_price IS NULL OR total_price = 0 THEN 1 END) as sem_price,
            COUNT(CASE WHEN base_price IS NULL OR base_price = 0 THEN 1 END) as sem_base_price
        FROM broker_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    print(f"\nBrokers 2025-2026:")
    print(f"  Total de reservas: {row[0]}")
    print(f"  Sem voucher: {row[1]} ({row[1]/row[0]*100:.1f}%)" if row[0] > 0 else "  Sem voucher: 0")
    print(f"  Sem price: {row[2]} ({row[2]/row[0]*100:.1f}%)" if row[0] > 0 else "  Sem price: 0")
    print(f"  Sem base_price: {row[3]} ({row[3]/row[0]*100:.1f}%)" if row[0] > 0 else "  Sem base_price: 0")
    
    # Mostrar exemplos de brokers sem base_price
    if row[3] > 0:
        print("\n" + "=" * 80)
        print("EXEMPLOS DE BROKERS SEM BASE_PRICE:")
        print("=" * 80)
        
        query = """
            SELECT 
                voucher_number,
                broker_name,
                pickup_date,
                total_price,
                base_price
            FROM broker_bookings
            WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
            AND (base_price IS NULL OR base_price = 0)
            ORDER BY pickup_date DESC
            LIMIT 10
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        print(f"\n{'Voucher':<20} {'Broker':<25} {'Data':<12} {'Total Price':<12} {'Base Price':<12}")
        print("-" * 90)
        
        for row in rows:
            voucher = row[0] or 'N/A'
            broker = row[1] or 'N/A'
            date = row[2]
            total = float(row[3]) if row[3] else 0
            base = float(row[4]) if row[4] else 0
            
            print(f"{voucher:<20} {broker:<25} {date} €{total:<11.2f} €{base:<11.2f}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_brokers_vs_commissioners()
