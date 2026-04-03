#!/usr/bin/env python3
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import _db_connect

try:
    con = _db_connect()
    
    # Check total commissions
    cur = con.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN commission_paid = 1 THEN 1 ELSE 0 END) as paid,
               SUM(commission_amount) as total_amount
        FROM commission_bookings 
        WHERE commission_amount > 0
    """)
    row = cur.fetchone()
    print(f"✅ Total de comissões: {row[0]}")
    print(f"✅ Pagas: {row[1]}")
    print(f"✅ Valor total: €{float(row[2]):.2f}" if row[2] else "✅ Valor total: €0.00")
    
    # Check March 2026 (previous month)
    cur = con.execute("""
        SELECT COUNT(*) as total,
               SUM(commission_amount) as total_amount
        FROM commission_bookings 
        WHERE commission_amount > 0
        AND (
            (pickup_date LIKE '2026-03-%')
            OR (strftime('%Y-%m', pickup_date) = '2026-03')
        )
    """)
    row = cur.fetchone()
    print(f"\n📅 Março 2026 (mês anterior):")
    print(f"   Comissões: {row[0]}")
    print(f"   Valor: €{float(row[1]):.2f}" if row[1] else "   Valor: €0.00")
    
    # Check 2026 total
    cur = con.execute("""
        SELECT COUNT(*) as total,
               SUM(commission_amount) as total_amount
        FROM commission_bookings 
        WHERE commission_amount > 0
        AND (
            (pickup_date LIKE '2026-%')
            OR (strftime('%Y', pickup_date) = '2026')
        )
    """)
    row = cur.fetchone()
    print(f"\n📅 2026 (ano atual):")
    print(f"   Comissões: {row[0]}")
    print(f"   Valor: €{float(row[1]):.2f}" if row[1] else "   Valor: €0.00")
    
    # Sample data
    cur = con.execute("""
        SELECT pickup_date, commission_amount, commission_paid
        FROM commission_bookings 
        WHERE commission_amount > 0
        ORDER BY pickup_date DESC
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"\n📋 Últimas 5 comissões:")
    for row in rows:
        status = "✅ Paga" if row[2] else "⏳ Não paga"
        print(f"   {row[0]}: €{float(row[1]):.2f} - {status}")
    
    con.close()
    print("\n✅ Diagnóstico completo!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
