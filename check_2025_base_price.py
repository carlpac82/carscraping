import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def check_2025_base_price():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAR ESTRUTURA DA TABELA commission_bookings")
    print("=" * 80)
    
    # Verificar colunas da tabela
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'commission_bookings'
        ORDER BY ordinal_position
    """
    
    cur.execute(query)
    columns = cur.fetchall()
    
    print("\nCOLUNAS DA TABELA:")
    print("-" * 80)
    for col in columns:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
    
    # Verificar dados de 2025
    print("\n" + "=" * 80)
    print("DADOS DE 2025 - PRIMEIROS 20 REGISTOS")
    print("=" * 80)
    
    query = """
        SELECT 
            cb.voucher_number,
            cb.pickup_date,
            cb.price,
            cb.base_price,
            cb.commission_amount,
            c.commission_rate,
            c.name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
        ORDER BY cb.pickup_date
        LIMIT 20
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Voucher':<20} {'Data':<12} {'Price':<10} {'Base Price':<12} {'Comissão':<10} {'Taxa':<8} {'Nome':<20}")
    print("-" * 120)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        date = row[1]
        price = float(row[2]) if row[2] else 0
        base_price = float(row[3]) if row[3] else 0
        commission = float(row[4]) if row[4] else 0
        rate = float(row[5]) if row[5] else 0
        name = row[6]
        
        # Calcular comissão esperada: (price / 1.23) * rate
        expected_commission = (price / 1.23) * rate if price > 0 else 0
        
        # Verificar se base_price está preenchido
        base_status = "✓" if base_price > 0 else "❌ VAZIO"
        
        # Verificar se comissão está correta
        comm_status = "✓" if abs(commission - expected_commission) < 0.01 else f"❌ ({expected_commission:.2f})"
        
        print(f"{voucher:<20} {date} €{price:<9.2f} €{base_price:<11.2f} €{commission:<9.2f} {rate:<7.2%} {name:<20} {base_status} {comm_status}")
    
    # Verificar quantos registos têm base_price NULL ou 0
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS DE BASE_PRICE EM 2025")
    print("=" * 80)
    
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN base_price IS NULL OR base_price = 0 THEN 1 END) as sem_base_price,
            COUNT(CASE WHEN base_price > 0 THEN 1 END) as com_base_price
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    print(f"\nTotal de registos: {row[0]}")
    print(f"Sem base_price: {row[1]} ({row[1]/row[0]*100:.1f}%)")
    print(f"Com base_price: {row[2]} ({row[2]/row[0]*100:.1f}%)")
    
    # Verificar se a comissão está calculada corretamente
    print("\n" + "=" * 80)
    print("VERIFICAR CÁLCULO DE COMISSÃO")
    print("=" * 80)
    
    query = """
        SELECT 
            cb.voucher_number,
            cb.price,
            cb.commission_amount,
            c.commission_rate,
            (cb.price / 1.23) * c.commission_rate as expected_commission
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
        AND cb.price > 0
        LIMIT 10
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Voucher':<20} {'Price':<10} {'Comissão':<12} {'Taxa':<8} {'Esperado':<12} {'Status':<10}")
    print("-" * 80)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        price = float(row[1]) if row[1] else 0
        commission = float(row[2]) if row[2] else 0
        rate = float(row[3]) if row[3] else 0
        expected = float(row[4]) if row[4] else 0
        
        status = "✓ OK" if abs(commission - expected) < 0.01 else "❌ ERRO"
        
        print(f"{voucher:<20} €{price:<9.2f} €{commission:<11.2f} {rate:<7.2%} €{expected:<11.2f} {status:<10}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_2025_base_price()
