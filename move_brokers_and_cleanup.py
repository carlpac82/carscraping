import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def move_brokers_and_cleanup():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("1. MOVER RESERVAS DE BROKERS PARA broker_bookings")
    print("=" * 80)
    
    # IDs dos brokers que estão incorretamente em commissioners
    broker_commissioner_ids = [246, 252]  # DISCOVERCARS-PREPAID, BROKERS-DIRECTOS
    
    # Buscar as reservas desses brokers
    query = """
        SELECT 
            cb.id,
            cb.commissioner_id,
            cb.voucher_number,
            cb.client_name,
            cb.pickup_date,
            cb.dropoff_date,
            cb.vehicle_group,
            cb.price,
            c.name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE cb.commissioner_id = ANY(%s)
    """
    
    cur.execute(query, (broker_commissioner_ids,))
    reservas = cur.fetchall()
    
    print(f"\n📋 Encontradas {len(reservas)} reservas para mover:")
    
    moved_count = 0
    
    for reserva in reservas:
        booking_id = reserva[0]
        commissioner_id = reserva[1]
        voucher = reserva[2]
        client_name = reserva[3]
        pickup_date = reserva[4]
        dropoff_date = reserva[5]
        vehicle_group = reserva[6]
        price = float(reserva[7]) if reserva[7] else 0
        broker_name = reserva[8]
        
        # Calcular dias
        days = 1
        if pickup_date and dropoff_date:
            days = (dropoff_date - pickup_date).days
        
        print(f"\n  Mover: {broker_name} - {voucher or 'N/A'} - {pickup_date} - €{price:.2f}")
        
        # Inserir em broker_bookings
        try:
            insert_query = """
                INSERT INTO broker_bookings (
                    broker_name, voucher_number, client_name, pickup_date, dropoff_date,
                    vehicle_group, days, total_price, status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """
            
            cur.execute(insert_query, (
                broker_name, voucher, client_name, pickup_date, dropoff_date,
                vehicle_group, days, price, 'confirmed'
            ))
            
            # Apagar de commission_bookings
            delete_query = "DELETE FROM commission_bookings WHERE id = %s"
            cur.execute(delete_query, (booking_id,))
            
            print(f"    ✅ Movida com sucesso")
            moved_count += 1
            
        except Exception as e:
            print(f"    ❌ Erro: {str(e)}")
    
    print(f"\n✅ Total movidas: {moved_count}")
    
    # 2. ELIMINAR RESERVA AP DE 03/04/2026
    print("\n" + "=" * 80)
    print("2. ELIMINAR RESERVA AP DE 03/04/2026")
    print("=" * 80)
    
    # Procurar a reserva AP com comissão €9.15 em 03/04/2026
    query = """
        SELECT 
            cb.id,
            cb.voucher_number,
            cb.pickup_date,
            cb.price,
            cb.base_price,
            cb.commission_amount,
            c.name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE cb.pickup_date = '2026-04-03'
        AND cb.commission_amount BETWEEN 9.10 AND 9.20
    """
    
    cur.execute(query)
    ap_reserva = cur.fetchone()
    
    if ap_reserva:
        booking_id = ap_reserva[0]
        voucher = ap_reserva[1]
        pickup_date = ap_reserva[2]
        price = float(ap_reserva[3]) if ap_reserva[3] else 0
        base_price = float(ap_reserva[4]) if ap_reserva[4] else 0
        commission = float(ap_reserva[5]) if ap_reserva[5] else 0
        name = ap_reserva[6]
        
        print(f"\n📋 Encontrada reserva:")
        print(f"  ID: {booking_id}")
        print(f"  Comissionista: {name}")
        print(f"  Voucher: {voucher or 'N/A'}")
        print(f"  Data: {pickup_date}")
        print(f"  Price: €{price:.2f}")
        print(f"  Base Price: €{base_price:.2f}")
        print(f"  Comissão: €{commission:.2f}")
        
        # Eliminar
        delete_query = "DELETE FROM commission_bookings WHERE id = %s"
        cur.execute(delete_query, (booking_id,))
        
        print(f"\n✅ Reserva eliminada")
    else:
        print("\n⚠️  Reserva AP de 03/04/2026 não encontrada")
    
    # 3. APAGAR BROKERS SEM RESERVAS DE commissioners
    print("\n" + "=" * 80)
    print("3. APAGAR BROKERS SEM RESERVAS DE commissioners")
    print("=" * 80)
    
    # Lista de IDs de brokers sem reservas
    broker_ids_to_delete = [191, 232, 235, 236, 237, 245, 253, 254]
    
    # Verificar se têm reservas
    query = """
        SELECT c.id, c.name, COUNT(cb.id) as count
        FROM commissioners c
        LEFT JOIN commission_bookings cb ON c.id = cb.commissioner_id
        WHERE c.id = ANY(%s)
        GROUP BY c.id, c.name
    """
    
    cur.execute(query, (broker_ids_to_delete,))
    brokers = cur.fetchall()
    
    deleted_count = 0
    
    for broker_id, name, count in brokers:
        if count == 0:
            delete_query = "DELETE FROM commissioners WHERE id = %s"
            cur.execute(delete_query, (broker_id,))
            print(f"  ✅ Apagado: {name} (ID: {broker_id})")
            deleted_count += 1
        else:
            print(f"  ⚠️  Mantido: {name} (ID: {broker_id}) - tem {count} reservas")
    
    # Também apagar os que foram movidos
    for broker_id in broker_commissioner_ids:
        query = "SELECT name FROM commissioners WHERE id = %s"
        cur.execute(query, (broker_id,))
        result = cur.fetchone()
        
        if result:
            name = result[0]
            delete_query = "DELETE FROM commissioners WHERE id = %s"
            cur.execute(delete_query, (broker_id,))
            print(f"  ✅ Apagado: {name} (ID: {broker_id}) - reservas movidas")
            deleted_count += 1
    
    print(f"\n✅ Total de brokers apagados: {deleted_count}")
    
    # Commit
    conn.commit()
    
    print("\n" + "=" * 80)
    print("RESUMO FINAL:")
    print("=" * 80)
    print(f"✅ Reservas movidas para broker_bookings: {moved_count}")
    print(f"✅ Reserva AP eliminada: {'Sim' if ap_reserva else 'Não encontrada'}")
    print(f"✅ Brokers apagados de commissioners: {deleted_count}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    move_brokers_and_cleanup()
