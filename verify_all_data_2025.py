import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== VERIFICAÇÃO COMPLETA DE DADOS 2025 ===\n")
    
    # Brokers por mês
    print("BROKERS POR MÊS:")
    cur.execute("""
        SELECT 
            EXTRACT(MONTH FROM pickup_date) as mes,
            COUNT(*) as total,
            SUM(total_price) as valor_total
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        GROUP BY EXTRACT(MONTH FROM pickup_date)
        ORDER BY mes
    """)
    
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    for row in cur.fetchall():
        print(f"  {month_names[int(row[0])-1]}: {row[1]} reservas, €{row[2]:.2f}")
    
    # Brokers por nome
    print("\nBROKERS POR NOME:")
    cur.execute("""
        SELECT broker_name, COUNT(*) as total, SUM(total_price) as valor_total
        FROM broker_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        GROUP BY broker_name 
        ORDER BY total DESC
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} reservas, €{row[2]:.2f}")
    
    # Comissionistas por mês
    print("\nCOMISSIONISTAS POR MÊS:")
    cur.execute("""
        SELECT 
            EXTRACT(MONTH FROM pickup_date) as mes,
            COUNT(*) as total,
            SUM(commission_amount) as comissao_total
        FROM commission_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        GROUP BY EXTRACT(MONTH FROM pickup_date)
        ORDER BY mes
    """)
    
    for row in cur.fetchall():
        print(f"  {month_names[int(row[0])-1]}: {row[1]} reservas, €{row[2]:.2f}")
    
    # Total geral
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE EXTRACT(YEAR FROM pickup_date) = 2025")
    total_brokers = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM commission_bookings WHERE EXTRACT(YEAR FROM pickup_date) = 2025")
    total_commissions = cur.fetchone()[0]
    
    print(f"\n=== TOTAIS ===")
    print(f"Total de brokers 2025: {total_brokers}")
    print(f"Total de comissionistas 2025: {total_commissions}")
    print(f"TOTAL GERAL: {total_brokers + total_commissions}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
