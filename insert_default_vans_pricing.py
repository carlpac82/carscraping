#!/usr/bin/env python3
"""
Insert default vans pricing into database
"""
import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print(f"🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Insert default vans pricing
    print("\n💾 Inserting default vans pricing...")
    cur.execute("""
        INSERT INTO vans_pricing (
            c3_1day, c3_2days, c3_3days,
            c4_1day, c4_2days, c4_3days,
            c5_1day, c5_2days, c5_3days,
            updated_at
        ) VALUES (
            112, 144, 180,
            152, 170, 210,
            175, 190, 240,
            NOW()
        )
    """)
    
    conn.commit()
    print("✅ Default vans pricing inserted successfully!")
    
    # Verify
    cur.execute("SELECT * FROM vans_pricing ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    print(f"\n📋 Verified:")
    print(f"  C3: 1day={row[1]}, 2days={row[2]}, 3days={row[3]}")
    print(f"  C4: 1day={row[4]}, 2days={row[5]}, 3days={row[6]}")
    print(f"  C5: 1day={row[7]}, 2days={row[8]}, 3days={row[9]}")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    cur.close()
    conn.close()
