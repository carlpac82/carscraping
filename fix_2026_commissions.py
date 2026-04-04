import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_2026_commissions():
    """
    Corrigir dados de 2026:
    1. Preencher base_price = price / 1.23
    2. Recalcular commission_amount = base_price × commission_rate
    """
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("CORRIGIR DADOS DE COMISSIONISTAS 2026")
    print("=" * 80)
    
    # Verificar estado atual
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN base_price IS NULL OR base_price = 0 THEN 1 END) as sem_base_price
        FROM commission_bookings
        WHERE EXTRACT(YEAR FROM pickup_date) = 2026
    """
    
    cur.execute(query)
    row = cur.fetchone()
    
    print(f"\n📋 Total de registos 2026: {row[0]}")
    print(f"   Sem base_price: {row[1]}")
    
    # Obter todos os registos de 2026
    query = """
        SELECT 
            cb.id,
            cb.price,
            cb.base_price,
            cb.commission_amount,
            c.commission_rate
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2026
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    updated_count = 0
    
    print("\nProcessando...")
    
    for row in rows:
        booking_id = row[0]
        price = float(row[1]) if row[1] else 0
        current_base_price = float(row[2]) if row[2] else 0
        current_commission = float(row[3]) if row[3] else 0
        commission_rate = float(row[4]) if row[4] else 0.15
        
        # Calcular base_price (price sem IVA)
        correct_base_price = price / 1.23
        
        # Calcular comissão correta: base_price × commission_rate
        correct_commission = correct_base_price * commission_rate
        
        # Verificar se precisa atualizar
        needs_update = False
        if abs(current_base_price - correct_base_price) > 0.01:
            needs_update = True
        if abs(current_commission - correct_commission) > 0.01:
            needs_update = True
        
        if needs_update:
            try:
                update_query = """
                    UPDATE commission_bookings 
                    SET base_price = %s,
                        commission_amount = %s
                    WHERE id = %s
                """
                cur.execute(update_query, (correct_base_price, correct_commission, booking_id))
                updated_count += 1
                
                if updated_count <= 10:
                    print(f"  ✓ ID {booking_id}: base_price=€{current_base_price:.2f} → €{correct_base_price:.2f}, comissão=€{current_commission:.2f} → €{correct_commission:.2f}")
                
            except Exception as e:
                print(f"  ❌ Erro ao atualizar ID {booking_id}: {str(e)}")
    
    if updated_count > 10:
        print(f"  ... e mais {updated_count - 10} registos atualizados")
    
    # Commit
    conn.commit()
    
    print(f"\n✅ Total de registos atualizados: {updated_count}")
    
    # Verificar resultado por mês
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO APÓS CORREÇÃO:")
    print("=" * 80)
    
    for month in [1, 2, 3]:
        month_names = ['Janeiro', 'Fevereiro', 'Março']
        
        query = """
            SELECT 
                COUNT(*) as count,
                SUM(price) as total_price,
                SUM(base_price) as total_base_price,
                SUM(commission_amount) as total_commission
            FROM commission_bookings
            WHERE EXTRACT(YEAR FROM pickup_date) = 2026
            AND EXTRACT(MONTH FROM pickup_date) = %s
        """
        
        cur.execute(query, (month,))
        row = cur.fetchone()
        
        count = row[0]
        total_price = float(row[1]) if row[1] else 0
        total_base_price = float(row[2]) if row[2] else 0
        total_commission = float(row[3]) if row[3] else 0
        
        print(f"\n{month_names[month-1]} 2026:")
        print(f"  Reservas: {count}")
        print(f"  Total Price (com IVA): €{total_price:.2f}")
        print(f"  Total Base Price (sem IVA): €{total_base_price:.2f}")
        print(f"  Total Comissão: €{total_commission:.2f}")
        
        # Verificar se cálculo está correto
        expected_base = total_price / 1.23
        if abs(total_base_price - expected_base) < 0.5:
            print(f"  ✓ Base price correto")
        else:
            print(f"  ❌ Base price incorreto (esperado: €{expected_base:.2f})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_2026_commissions()
