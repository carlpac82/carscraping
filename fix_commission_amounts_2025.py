import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_commission_amounts():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("CORRIGIR VALORES DE COMISSÃO PARA 2025")
    print("=" * 80)
    
    # Obter todos os registos de 2025
    query = """
        SELECT 
            cb.id,
            cb.price,
            cb.commission_amount,
            c.commission_rate,
            c.name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE EXTRACT(YEAR FROM cb.pickup_date) = 2025
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n📋 Total de registos encontrados: {len(rows)}")
    
    updated_count = 0
    errors = []
    
    for row in rows:
        booking_id = row[0]
        price = float(row[1]) if row[1] else 0
        current_commission = float(row[2]) if row[2] else 0
        commission_rate = float(row[3]) if row[3] else 0
        commissioner_name = row[4]
        
        # Calcular comissão correta
        # Se a taxa está em formato 15.0, converter para 0.15
        if commission_rate > 1:
            correct_rate = commission_rate / 100
        else:
            correct_rate = commission_rate
            
        correct_commission = price * correct_rate
        
        # Verificar se precisa atualizar
        if abs(current_commission - correct_commission) > 0.01:
            try:
                update_query = """
                    UPDATE commission_bookings 
                    SET commission_amount = %s 
                    WHERE id = %s
                """
                cur.execute(update_query, (correct_commission, booking_id))
                updated_count += 1
                
                if updated_count <= 10:
                    print(f"  ✓ ID {booking_id} ({commissioner_name}): €{current_commission:.2f} → €{correct_commission:.2f}")
                
            except Exception as e:
                errors.append(f"Erro ao atualizar ID {booking_id}: {str(e)}")
    
    if updated_count > 10:
        print(f"  ... e mais {updated_count - 10} registos atualizados")
    
    # Commit das alterações
    conn.commit()
    
    print(f"\n✅ Total de registos atualizados: {updated_count}")
    
    if errors:
        print(f"\n❌ Erros encontrados: {len(errors)}")
        for error in errors[:5]:
            print(f"  - {error}")
    
    # Verificar totais após correção
    print("\n" + "=" * 80)
    print("TOTAIS APÓS CORREÇÃO:")
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
    fix_commission_amounts()
