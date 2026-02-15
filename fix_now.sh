#!/bin/bash
# Quick fix script to mark 40-XM-45 inspection as replaced

python3 << 'EOF'
import psycopg2

try:
    conn = psycopg2.connect(
        host='autorally.proxy.rlwy.net',
        port=21432,
        database='railway',
        user='postgres',
        password='tJXMuELXzfSBqHbJIGvxnzVpYJgRGHWu'
    )
    
    cur = conn.cursor()
    
    # Mark 40-XM-45 check-in as replaced
    cur.execute("""
        UPDATE vehicle_inspections
        SET status = 'replaced'
        WHERE contract_number LIKE '06761%'
          AND vehicle_plate = '40-XM-45'
          AND inspection_type = 'checkin'
          AND COALESCE(status, '') != 'replaced'
    """)
    
    rows = cur.rowcount
    print(f"✅ Marked {rows} inspection(s) as 'replaced'")
    
    conn.commit()
    
    # Verify it worked
    cur.execute("""
        SELECT inspection_number, status
        FROM vehicle_inspections
        WHERE contract_number LIKE '06761%'
          AND vehicle_plate = '40-XM-45'
          AND inspection_type = 'checkin'
    """)
    
    for row in cur.fetchall():
        print(f"   {row[0]}: status={row[1]}")
    
    cur.close()
    conn.close()
    
    print("\n✅ Done! 40-XM-45 should now appear in the swap list.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
EOF
