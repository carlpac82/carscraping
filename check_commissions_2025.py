import psycopg2
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check total commissions in 2025
    print("\n=== VERIFICAÇÃO DE COMISSÕES 2025 ===\n")
    
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(commission_amount) as total_commission,
            COUNT(CASE WHEN commission_paid = true THEN 1 END) as paid_count,
            SUM(CASE WHEN commission_paid = true THEN commission_amount ELSE 0 END) as paid_amount
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        AND commission_amount > 0
    """)
    
    row = cur.fetchone()
    print(f"Total de registos 2025: {row[0]}")
    print(f"Total de comissões 2025: €{row[1]:.2f}" if row[1] else "€0.00")
    print(f"Comissões pagas: {row[2]} (€{row[3]:.2f})" if row[3] else f"Comissões pagas: {row[2]} (€0.00)")
    
    # Check by month
    print("\n=== POR MÊS ===\n")
    cur.execute("""
        SELECT 
            EXTRACT(MONTH FROM pickup_date) as month,
            COUNT(*) as total,
            SUM(commission_amount) as total_commission
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        AND commission_amount > 0
        GROUP BY EXTRACT(MONTH FROM pickup_date)
        ORDER BY month
    """)
    
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    for row in cur.fetchall():
        month_idx = int(row[0]) - 1
        print(f"{months[month_idx]}: {row[1]} reservas, €{row[2]:.2f}")
    
    # Check sample records
    print("\n=== EXEMPLOS DE REGISTOS ===\n")
    cur.execute("""
        SELECT 
            voucher_number,
            client_name,
            pickup_date,
            commission_amount,
            commission_paid
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
        AND commission_amount > 0
        ORDER BY pickup_date DESC
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        status = "PAGA" if row[4] else "NÃO PAGA"
        print(f"Voucher: {row[0]}, Cliente: {row[1]}, Data: {row[2]}, Comissão: €{row[3]:.2f}, Status: {status}")
    
    cur.close()
    conn.close()
    print("\n✓ Verificação concluída")
    
except Exception as e:
    print(f"✗ Erro: {e}")
