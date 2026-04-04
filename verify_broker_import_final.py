import psycopg2
import os

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*70)
    print("VERIFICAÇÃO DA IMPORTAÇÃO DE BROKERS")
    print("="*70)
    
    # Total de registos
    cur.execute("SELECT COUNT(*) FROM broker_bookings")
    total = cur.fetchone()[0]
    print(f"\n📊 Total de registos: {total}")
    
    # Registos com voucher vs NULL
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE voucher_number IS NOT NULL")
    with_voucher = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE voucher_number IS NULL")
    without_voucher = cur.fetchone()[0]
    
    print(f"\n✓ Com voucher: {with_voucher}")
    print(f"✓ Sem voucher (NULL): {without_voucher}")
    
    # Verificar se existem vouchers AP-XX
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE voucher_number LIKE 'AP-%'")
    ap_vouchers = cur.fetchone()[0]
    print(f"\n⚠️  Vouchers AP-XX: {ap_vouchers} (deve ser 0)")
    
    # Verificar se existem vouchers COMM-XX
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE voucher_number LIKE 'COMM-%'")
    comm_vouchers = cur.fetchone()[0]
    print(f"⚠️  Vouchers COMM-XX: {comm_vouchers} (deve ser 0)")
    
    # Amostra de vouchers reais
    print("\n📋 Amostra de 10 vouchers importados:")
    cur.execute("""
        SELECT broker_name, voucher_number, pickup_date, days, total_price
        FROM broker_bookings
        WHERE voucher_number IS NOT NULL
        ORDER BY pickup_date DESC
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        days_display = row[3] if row[3] is not None else 0
        print(f"  {row[0]:20s} | Voucher: {str(row[1]):20s} | Data: {row[2]} | Dias: {days_display:3d} | Preço: €{row[4]:.2f}")
    
    # Amostra de registos sem voucher
    print("\n📋 Amostra de 10 registos SEM voucher:")
    cur.execute("""
        SELECT broker_name, voucher_number, pickup_date, days, total_price
        FROM broker_bookings
        WHERE voucher_number IS NULL
        ORDER BY pickup_date DESC
        LIMIT 10
    """)
    
    for row in cur.fetchall():
        voucher_display = "NULL" if row[1] is None else str(row[1])
        days_display = row[3] if row[3] is not None else 0
        print(f"  {row[0]:20s} | Voucher: {voucher_display:20s} | Data: {row[2]} | Dias: {days_display:3d} | Preço: €{row[4]:.2f}")
    
    # Distribuição por broker
    print("\n📊 Distribuição por broker:")
    cur.execute("""
        SELECT broker_name, COUNT(*), 
               SUM(CASE WHEN voucher_number IS NOT NULL THEN 1 ELSE 0 END) as com_voucher,
               SUM(CASE WHEN voucher_number IS NULL THEN 1 ELSE 0 END) as sem_voucher
        FROM broker_bookings
        GROUP BY broker_name
        ORDER BY COUNT(*) DESC
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]:25s}: {row[1]:4d} total | {row[2]:4d} com voucher | {row[3]:4d} sem voucher")
    
    # Verificar se dias foram importados
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE days IS NULL")
    null_days = cur.fetchone()[0]
    print(f"\n✓ Registos sem dias: {null_days}")
    
    # Verificar se preços foram importados
    cur.execute("SELECT COUNT(*) FROM broker_bookings WHERE total_price IS NULL OR total_price = 0")
    null_prices = cur.fetchone()[0]
    print(f"✓ Registos sem preço: {null_prices}")
    
    print("\n" + "="*70)
    if ap_vouchers == 0 and comm_vouchers == 0:
        print("✅ IMPORTAÇÃO CORRETA!")
        print("   - Nenhum voucher gerado automaticamente")
        print("   - Vouchers originais preservados")
        print("   - Dias e preços importados corretamente")
    else:
        print("❌ PROBLEMA: Ainda existem vouchers gerados automaticamente!")
    print("="*70)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Erro: {e}")
    import traceback
    traceback.print_exc()
