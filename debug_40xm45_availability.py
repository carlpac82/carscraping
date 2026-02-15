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
print("🔍 DEBUG: Checking why 40-XM-45 is not available for swap")
print("=" * 80)

# 1. Check rental_agreements for 40-XM-45
print("\n1️⃣ Rental Agreements with 40-XM-45:")
cur.execute("""
    SELECT rental_agreement_number, license_plate, created_at
    FROM rental_agreements
    WHERE license_plate = '40-XM-45'
    ORDER BY created_at DESC
""")
ras = cur.fetchall()
for ra in ras:
    print(f"   RA: {ra[0]}, Plate: {ra[1]}, Created: {ra[2]}")
if not ras:
    print("   ❌ No RAs found with license_plate = '40-XM-45'")

# 2. Check vehicle_inspections for 40-XM-45
print("\n2️⃣ Vehicle Inspections for 40-XM-45:")
cur.execute("""
    SELECT inspection_number, contract_number, inspection_type, status, created_at
    FROM vehicle_inspections
    WHERE vehicle_plate = '40-XM-45'
    ORDER BY created_at DESC
""")
inspections = cur.fetchall()
for insp in inspections:
    print(f"   {insp[0]}: RA={insp[1]}, Type={insp[2]}, Status={insp[3]}, Created={insp[4]}")
if not inspections:
    print("   ❌ No inspections found for 40-XM-45")

# 3. Check if 40-XM-45 has active check-in without checkout
print("\n3️⃣ Active Check-ins (no checkout) for 40-XM-45:")
cur.execute("""
    SELECT DISTINCT ra.rental_agreement_number, ra.license_plate
    FROM rental_agreements ra
    WHERE ra.license_plate = '40-XM-45'
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
""")
active = cur.fetchall()
for a in active:
    print(f"   ⚠️ RA {a[0]} has active check-in without checkout (blocks availability)")
if not active:
    print("   ✅ No active check-ins blocking availability")

# 4. Check vehicle_swaps for RA 06761
print("\n4️⃣ Vehicle Swaps for RA 06761:")
cur.execute("""
    SELECT id, swap_datetime, old_plate, new_plate, employee_name
    FROM vehicle_swaps
    WHERE rental_agreement_number = '06761'
    ORDER BY swap_datetime DESC
""")
swaps = cur.fetchall()
for swap in swaps:
    print(f"   Swap #{swap[0]}: {swap[2]} → {swap[3]} at {swap[1]} by {swap[4]}")
if not swaps:
    print("   ❌ No swaps found for RA 06761")

# 5. Check vehicles table for 40-XM-45
print("\n5️⃣ Vehicle 40-XM-45 in fleet:")
cur.execute("""
    SELECT matricula, marca, modelo, km_atual, nivel_combustivel, status
    FROM vehicles
    WHERE matricula = '40-XM-45'
""")
vehicle = cur.fetchone()
if vehicle:
    print(f"   Plate: {vehicle[0]}, Brand: {vehicle[1]}, Model: {vehicle[2]}")
    print(f"   KM: {vehicle[3]}, Fuel: {vehicle[4]}, Status: {vehicle[5]}")
else:
    print("   ❌ Vehicle 40-XM-45 not found in vehicles table")

# 6. Run the exact query used by /api/vehicles/available
print("\n6️⃣ Running availability query (should 40-XM-45 appear?):")
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
    print(f"   ✅ 40-XM-45 IS available: {available[0]} - {available[1]} {available[2]}")
else:
    print("   ❌ 40-XM-45 is NOT available (blocked by query)")

# 7. Check what's blocking it
print("\n7️⃣ What's blocking 40-XM-45?")
cur.execute("""
    SELECT DISTINCT ra.rental_agreement_number, ra.license_plate
    FROM rental_agreements ra
    WHERE ra.license_plate = '40-XM-45'
    AND ra.license_plate IS NOT NULL
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
""")
blocking = cur.fetchall()
if blocking:
    for b in blocking:
        print(f"   ⚠️ Blocked by RA {b[0]} (license_plate = {b[1]})")
        # Show the check-in that's blocking
        cur.execute("""
            SELECT inspection_number, inspection_type, status, created_at
            FROM vehicle_inspections
            WHERE contract_number LIKE %s
            AND vehicle_plate = '40-XM-45'
            ORDER BY created_at DESC
        """, (f"{b[0]}%",))
        blocking_inspections = cur.fetchall()
        for bi in blocking_inspections:
            print(f"      - {bi[0]}: Type={bi[1]}, Status={bi[2]}, Created={bi[3]}")
else:
    print("   ✅ Nothing blocking (should be available)")

print("\n" + "=" * 80)

cur.close()
conn.close()
