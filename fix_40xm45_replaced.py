import psycopg2
import os

# Railway PostgreSQL connection
conn = psycopg2.connect(
    host="autorally.proxy.rlwy.net",
    port=21432,
    database="railway",
    user="postgres",
    password="tJXMuELXzfSBqHbJIGvxnzVpYJgRGHWu"
)

cur = conn.cursor()

print("=" * 80)
print("🔧 FIX: Marking 40-XM-45 check-in as 'replaced' for RA 06761")
print("=" * 80)

# Mark the old check-in as replaced
cur.execute("""
    UPDATE vehicle_inspections
    SET status = 'replaced'
    WHERE contract_number LIKE '06761%'
      AND vehicle_plate = '40-XM-45'
      AND inspection_type = 'checkin'
      AND COALESCE(status, '') != 'replaced'
""")

rows_updated = cur.rowcount
print(f"\n✅ Updated {rows_updated} inspection(s) to status='replaced'")

if rows_updated > 0:
    # Show what was updated
    cur.execute("""
        SELECT inspection_number, contract_number, vehicle_plate, inspection_type, status, created_at
        FROM vehicle_inspections
        WHERE contract_number LIKE '06761%'
          AND vehicle_plate = '40-XM-45'
          AND inspection_type = 'checkin'
        ORDER BY created_at DESC
    """)
    inspections = cur.fetchall()
    print("\n📋 Inspections for 40-XM-45 in RA 06761:")
    for insp in inspections:
        print(f"   {insp[0]}: RA={insp[1]}, Plate={insp[2]}, Type={insp[3]}, Status={insp[4]}")

conn.commit()
print("\n💾 Changes committed!")

# Verify 40-XM-45 is now available
print("\n🔍 Checking if 40-XM-45 is now available...")
cur.execute("""
    SELECT DISTINCT v.matricula, v.marca, v.modelo
    FROM vehicles v
    WHERE v.matricula = '40-XM-45'
    AND v.matricula NOT IN (
        SELECT DISTINCT ra.license_plate
        FROM rental_agreements ra
        WHERE ra.license_plate IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM vehicle_inspections vi
            WHERE vi.contract_number LIKE ra.rental_agreement_number || '%'
            AND vi.inspection_type = 'checkin'
            AND COALESCE(vi.status, '') != 'replaced'
        )
        AND NOT EXISTS (
            SELECT 1 FROM vehicle_inspections vi
            WHERE vi.contract_number LIKE ra.rental_agreement_number || '%'
            AND vi.inspection_type = 'checkout'
        )
    )
""")
available = cur.fetchone()
if available:
    print(f"   ✅ 40-XM-45 IS NOW AVAILABLE: {available[0]} - {available[1]} {available[2]}")
else:
    print("   ❌ 40-XM-45 is still NOT available")

print("\n" + "=" * 80)

cur.close()
conn.close()
