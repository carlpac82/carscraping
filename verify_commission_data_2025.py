import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def verify_commission_data():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAÇÃO DE DADOS DE COMISSIONISTAS 2025")
    print("=" * 80)
    
    # Verificar alguns registos de exemplo de 2025
    query = """
        SELECT 
            cb.voucher_number,
            cb.pickup_date,
            cb.price,
            cb.commission_amount,
            c.commission_rate,
            c.name as commissioner_name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
        ORDER BY cb.pickup_date
        LIMIT 20
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print("\n📋 PRIMEIROS 20 REGISTOS DE 2025:")
    print("-" * 80)
    print(f"{'Voucher':<15} {'Data':<12} {'Price':<10} {'Comissão':<10} {'Taxa':<8} {'Comissionista':<20}")
    print("-" * 80)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        pickup_date = row[1]
        price = float(row[2]) if row[2] else 0
        commission = float(row[3]) if row[3] else 0
        rate = float(row[4]) if row[4] else 0
        name = row[5]
        
        # Calcular comissão esperada
        expected_commission = price * rate
        
        # Verificar se está correto
        status = "✓" if abs(commission - expected_commission) < 0.01 else "✗ ERRO"
        
        print(f"{voucher:<15} {pickup_date} {price:<10.2f} {commission:<10.2f} {rate:<8.2%} {name:<20} {status}")
    
    # Verificar totais por mês
    print("\n" + "=" * 80)
    print("TOTAIS POR MÊS EM 2025:")
    print("=" * 80)
    
    query = """
        SELECT 
            EXTRACT(MONTH FROM cb.pickup_date) as month,
            COUNT(*) as count,
            SUM(cb.price) as total_price,
            SUM(cb.commission_amount) as total_commission
        FROM commission_bookings cb
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
        GROUP BY EXTRACT(MONTH FROM cb.pickup_date)
        ORDER BY month
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Mês':<10} {'Reservas':<10} {'Total Price':<15} {'Total Comissão':<15}")
    print("-" * 80)
    
    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for row in rows:
        month_num = int(row[0])
        month_name = months[month_num - 1]
        count = row[1]
        total_price = float(row[2]) if row[2] else 0
        total_commission = float(row[3]) if row[3] else 0
        
        print(f"{month_name:<10} {count:<10} €{total_price:<14.2f} €{total_commission:<14.2f}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_commission_data()
