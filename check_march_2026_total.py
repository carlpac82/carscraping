import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def check_march_2026_total():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAR TOTAL DE COMISSÕES MARÇO 2026")
    print("=" * 80)
    
    # Total de todas as comissões de março 2026
    query = """
        SELECT 
            COUNT(*) as count,
            SUM(commission_amount) as total_commission,
            SUM(CASE WHEN commission_paid = true THEN commission_amount ELSE 0 END) as paid,
            SUM(CASE WHEN commission_paid IS NULL OR commission_paid = false THEN commission_amount ELSE 0 END) as unpaid
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2026
        AND EXTRACT(MONTH FROM pickup_date) = 3
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    count = row[0]
    total = float(row[1]) if row[1] else 0
    paid = float(row[2]) if row[2] else 0
    unpaid = float(row[3]) if row[3] else 0
    
    print(f"\nMarço 2026:")
    print(f"  Total de reservas: {count}")
    print(f"  Total de comissões: €{total:.2f}")
    print(f"  Comissões pagas: €{paid:.2f}")
    print(f"  Comissões por pagar: €{unpaid:.2f}")
    
    # Verificar alguns registos
    print("\n" + "=" * 80)
    print("EXEMPLOS DE REGISTOS:")
    print("=" * 80)
    
    query = """
        SELECT 
            cb.voucher_number,
            cb.pickup_date,
            cb.price,
            cb.base_price,
            cb.commission_amount,
            cb.commission_paid,
            c.name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2026
        AND EXTRACT(MONTH FROM cb.pickup_date) = 3
        ORDER BY cb.pickup_date
        LIMIT 10
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Voucher':<20} {'Data':<12} {'Price':<10} {'Base':<10} {'Comissão':<10} {'Pago':<8} {'Nome':<20}")
    print("-" * 110)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        date = row[1]
        price = float(row[2]) if row[2] else 0
        base = float(row[3]) if row[3] else 0
        commission = float(row[4]) if row[4] else 0
        paid_status = 'SIM' if row[5] else 'NÃO'
        name = row[6]
        
        print(f"{voucher:<20} {date} €{price:<9.2f} €{base:<9.2f} €{commission:<9.2f} {paid_status:<8} {name:<20}")
    
    # Verificar se o valor anterior era diferente
    print("\n" + "=" * 80)
    print("NOTA:")
    print("=" * 80)
    print(f"O valor atual de comissões por pagar em Março 2026 é: €{unpaid:.2f}")
    print(f"\nAntes da correção, o valor estava errado porque:")
    print(f"  - commission_amount estava calculado como: price × 0.15")
    print(f"  - Deveria ser: (price / 1.23) × 0.15")
    print(f"\nO valor de €300+ que aparecia antes estava ERRADO.")
    print(f"O valor correto é €{unpaid:.2f}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_march_2026_total()
