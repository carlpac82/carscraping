import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def verify_jan_feb_2026():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAR DADOS DE JANEIRO E FEVEREIRO 2026")
    print("=" * 80)
    
    for month in [1, 2]:
        month_name = 'Janeiro' if month == 1 else 'Fevereiro'
        
        query = """
            SELECT 
                COUNT(*) as count,
                SUM(price) as total_price,
                SUM(commission_amount) as total_commission
            FROM commission_bookings
            WHERE EXTRACT(YEAR FROM pickup_date) = 2026
            AND EXTRACT(MONTH FROM pickup_date) = %s
        """
        
        cur.execute(query, (month,))
        row = cur.fetchone()
        
        count = row[0]
        total_price = float(row[1]) if row[1] else 0
        total_commission = float(row[2]) if row[2] else 0
        
        print(f"\n{month_name} 2026:")
        print(f"  Reservas: {count}")
        print(f"  Total Price: €{total_price:.2f}")
        print(f"  Total Comissão: €{total_commission:.2f}")
        
        # Mostrar alguns exemplos
        query = """
            SELECT 
                cb.voucher_number,
                cb.pickup_date,
                cb.price,
                cb.commission_amount,
                c.name
            FROM commission_bookings cb
            JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2026
            AND EXTRACT(MONTH FROM cb.pickup_date) = %s
            ORDER BY cb.pickup_date
            LIMIT 5
        """
        
        cur.execute(query, (month,))
        rows = cur.fetchall()
        
        print(f"\n  Exemplos:")
        for row in rows:
            voucher = row[0] or 'N/A'
            date = row[1]
            price = float(row[2]) if row[2] else 0
            commission = float(row[3]) if row[3] else 0
            name = row[4]
            
            print(f"    {date} - {name}: €{price:.2f} (comissão: €{commission:.2f})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify_jan_feb_2026()
