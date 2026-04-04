import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n=== VERIFICAÇÃO DE COMISSÕES 2026 ===\n")
    
    # Verificar comissões de 2026
    cur.execute("""
        SELECT 
            EXTRACT(MONTH FROM pickup_date) as mes,
            COUNT(*) as total,
            SUM(price) as valor_total,
            SUM(commission_amount) as comissao_total
        FROM commission_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2026
        GROUP BY EXTRACT(MONTH FROM pickup_date)
        ORDER BY mes
    """)
    
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    print("COMISSIONISTAS 2026 POR MÊS:")
    results = cur.fetchall()
    if results:
        for row in results:
            print(f"  {month_names[int(row[0])-1]}: {row[1]} reservas, Valor: €{row[2]:.2f}, Comissão: €{row[3]:.2f}")
    else:
        print("  Nenhum registo encontrado para 2026")
    
    # Ver exemplos de Janeiro, Fevereiro e Março 2026
    print("\n=== EXEMPLOS DE REGISTOS 2026 ===")
    cur.execute("""
        SELECT 
            voucher_number,
            client_name,
            pickup_date,
            price,
            commission_rate,
            commission_amount
        FROM commission_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2026
        AND EXTRACT(MONTH FROM pickup_date) IN (1, 2, 3)
        ORDER BY pickup_date
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[2]}, Preço: €{row[3]:.2f}, Taxa: {row[4]}%, Comissão: €{row[5]:.2f}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erro: {e}")
