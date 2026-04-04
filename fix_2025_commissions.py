import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_2025_commissions():
    """
    Corrigir dados de 2025:
    1. Preencher base_price = price / 1.23
    2. Recalcular commission_amount = base_price × commission_rate
    """
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("CORRIGIR DADOS DE COMISSIONISTAS 2025")
    print("=" * 80)
    
    # Obter todos os registos de 2025
    query = """
        SELECT 
            cb.id,
            cb.price,
            cb.commission_amount,
            c.commission_rate
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n📋 Total de registos encontrados: {len(rows)}")
    
    updated_count = 0
    
    print("\nProcessando...")
    
    for row in rows:
        booking_id = row[0]
        price = float(row[1]) if row[1] else 0
        current_commission = float(row[2]) if row[2] else 0
        commission_rate = float(row[3]) if row[3] else 0.15
        
        # Calcular base_price (price sem IVA)
        base_price = price / 1.23
        
        # Calcular comissão correta: base_price × commission_rate
        correct_commission = base_price * commission_rate
        
        # Atualizar na BD
        try:
            update_query = """
                UPDATE commission_bookings 
                SET base_price = %s,
                    commission_amount = %s
                WHERE id = %s
            """
            cur.execute(update_query, (base_price, correct_commission, booking_id))
            updated_count += 1
            
            if updated_count <= 10:
                print(f"  ✓ ID {booking_id}: price=€{price:.2f} → base_price=€{base_price:.2f}, comissão=€{current_commission:.2f} → €{correct_commission:.2f}")
            
        except Exception as e:
            print(f"  ❌ Erro ao atualizar ID {booking_id}: {str(e)}")
    
    if updated_count > 10:
        print(f"  ... e mais {updated_count - 10} registos atualizados")
    
    # Commit
    conn.commit()
    
    print(f"\n✅ Total de registos atualizados: {updated_count}")
    
    # Verificar resultado
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO APÓS CORREÇÃO:")
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
        LIMIT 10
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'Voucher':<20} {'Data':<12} {'Price':<10} {'Base Price':<12} {'Comissão':<10} {'Taxa':<8} {'Status':<10}")
    print("-" * 100)
    
    for row in rows:
        voucher = row[0] or 'N/A'
        date = row[1]
        price = float(row[2]) if row[2] else 0
        base_price = float(row[3]) if row[3] else 0
        commission = float(row[4]) if row[4] else 0
        rate = float(row[5]) if row[5] else 0
        name = row[6]
        
        # Verificar cálculo
        expected_base = price / 1.23
        expected_comm = expected_base * rate
        
        base_ok = abs(base_price - expected_base) < 0.01
        comm_ok = abs(commission - expected_comm) < 0.01
        
        status = "✓ OK" if (base_ok and comm_ok) else "❌ ERRO"
        
        print(f"{voucher:<20} {date} €{price:<9.2f} €{base_price:<11.2f} €{commission:<9.2f} {rate:<7.2%} {status:<10}")
    
    # Totais
    query = """
        SELECT 
            COUNT(*) as count,
            SUM(price) as total_price,
            SUM(base_price) as total_base_price,
            SUM(commission_amount) as total_commission
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    print(f"\n📊 TOTAIS 2025:")
    print(f"  Reservas: {row[0]}")
    print(f"  Total Price (com IVA): €{float(row[1]) if row[1] else 0:.2f}")
    print(f"  Total Base Price (sem IVA): €{float(row[2]) if row[2] else 0:.2f}")
    print(f"  Total Comissão: €{float(row[3]) if row[3] else 0:.2f}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_2025_commissions()
