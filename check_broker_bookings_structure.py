import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def check_broker_bookings_structure():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("ESTRUTURA DA TABELA broker_bookings")
    print("=" * 80)
    
    # Verificar colunas da tabela
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'broker_bookings'
        ORDER BY ordinal_position
    """
    
    cur.execute(query)
    columns = cur.fetchall()
    
    print("\nCOLUNAS DA TABELA:")
    print("-" * 80)
    for col in columns:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
    
    # Verificar dados de exemplo
    print("\n" + "=" * 80)
    print("EXEMPLOS DE DADOS (2025-2026):")
    print("=" * 80)
    
    query = """
        SELECT 
            voucher_number,
            broker_name,
            pickup_date,
            total_price,
            days
        FROM broker_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
        ORDER BY pickup_date DESC
        LIMIT 10
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Voucher':<20} {'Broker':<25} {'Data':<12} {'Total Price':<12} {'Dias':<6}")
    print("-" * 85)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        broker = row[1] or 'N/A'
        date = row[2]
        total = float(row[3]) if row[3] else 0
        days = row[4] if row[4] else 0
        
        print(f"{voucher:<20} {broker:<25} {date} €{total:<11.2f} {days:<6}")
    
    # Verificar estatísticas
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS 2025-2026:")
    print("=" * 80)
    
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN voucher_number IS NULL OR voucher_number = '' THEN 1 END) as sem_voucher,
            COUNT(CASE WHEN total_price IS NULL OR total_price = 0 THEN 1 END) as sem_price
        FROM broker_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) IN (2025, 2026)
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    print(f"\nTotal de reservas: {row[0]}")
    print(f"Sem voucher: {row[1]} ({row[1]/row[0]*100:.1f}%)" if row[0] > 0 else "Sem voucher: 0")
    print(f"Sem price: {row[2]} ({row[2]/row[0]*100:.1f}%)" if row[0] > 0 else "Sem price: 0")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_broker_bookings_structure()
