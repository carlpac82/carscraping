import psycopg2
import sys

# Railway PostgreSQL connection
try:
    conn = psycopg2.connect(
        host="autorally.proxy.rlwy.net",
        port=21432,
        database="railway",
        user="postgres",
        password="tJXMuELXzfSBqHbJIGvxnzVpYJgRGHWu"
    )
    cur = conn.cursor()
    
    print("=" * 100)
    print("🔍 DEEP DEBUG: Why 40-XM-45 is not available")
    print("=" * 100)
    
    # 1. Check rental_agreements for 40-XM-45
    print("\n1️⃣ RENTAL AGREEMENTS with license_plate = '40-XM-45':")
    cur.execute("""
        SELECT rental_agreement_number, license_plate, created_at
        FROM rental_agreements
        WHERE license_plate = '40-XM-45'
        ORDER BY created_at DESC
    """)
    ras_with_40 = cur.fetchall()
    if ras_with_40:
        for ra in ras_with_40:
            print(f"   ✅ RA: {ra[0]}, Plate: {ra[1]}, Created: {ra[2]}")
    else:
        print("   ❌ NO rental_agreements with license_plate = '40-XM-45'")
    
    # 2. Check RA 06761 current state
    print("\n2️⃣ RENTAL AGREEMENT 06761 current state:")
    cur.execute("""
        SELECT rental_agreement_number, license_plate, created_at
        FROM rental_agreements
        WHERE rental_agreement_number = '06761'
    """)
    ra_06761 = cur.fetchone()
    if ra_06761:
        print(f"   RA: {ra_06761[0]}, Current Plate: {ra_06761[1]}, Created: {ra_06761[2]}")
    else:
        print("   ❌ RA 06761 not found")
    
    # 3. Check ALL inspections for contract 06761
    print("\n3️⃣ ALL INSPECTIONS for contract 06761:")
    cur.execute("""
        SELECT inspection_number, vehicle_plate, inspection_type, status, created_at
        FROM vehicle_inspections
        WHERE contract_number LIKE '06761%'
        ORDER BY created_at DESC
    """)
    inspections = cur.fetchall()
    if inspections:
        for insp in inspections:
            status_emoji = "✅" if insp[3] == 'replaced' else "⚠️" if insp[3] else "❓"
            print(f"   {status_emoji} {insp[0]}: Plate={insp[1]}, Type={insp[2]}, Status={insp[3] or 'NULL'}, Created={insp[4]}")
    else:
        print("   ❌ No inspections found for contract 06761")
    
    # 4. Run the EXACT subquery that blocks availability
    print("\n4️⃣ BLOCKING QUERY - Does 40-XM-45 appear in the exclusion list?")
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
        print("   ⚠️ YES - 40-XM-45 IS BLOCKED by:")
        for b in blocking:
            print(f"      RA: {b[0]}, Plate: {b[1]}")
    else:
        print("   ✅ NO - 40-XM-45 is NOT in the blocking list")
    
    # 5. Check if 40-XM-45 exists in vehicles table
    print("\n5️⃣ VEHICLE 40-XM-45 in vehicles table:")
    cur.execute("""
        SELECT matricula, marca, modelo, status, grupo
        FROM vehicles
        WHERE matricula = '40-XM-45'
    """)
    vehicle = cur.fetchone()
    if vehicle:
        print(f"   ✅ Plate: {vehicle[0]}, Brand: {vehicle[1]}, Model: {vehicle[2]}, Status: {vehicle[3]}, Group: {vehicle[4]}")
    else:
        print("   ❌ Vehicle 40-XM-45 NOT FOUND in vehicles table")
    
    # 6. Run the FULL availability query for 40-XM-45
    print("\n6️⃣ FULL AVAILABILITY QUERY - Should 40-XM-45 be available?")
    cur.execute("""
        SELECT DISTINCT v.matricula, v.marca, v.modelo, v.grupo
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
        AND v.matricula IS NOT NULL
    """)
    available = cur.fetchone()
    if available:
        print(f"   ✅ YES - 40-XM-45 IS AVAILABLE: {available[0]} - {available[1]} {available[2]} (Group {available[3]})")
    else:
        print("   ❌ NO - 40-XM-45 is NOT available")
    
    # 7. Check vehicle_swaps table
    print("\n7️⃣ VEHICLE SWAPS for RA 06761:")
    cur.execute("""
        SELECT id, swap_datetime, old_plate, new_plate, employee_name
        FROM vehicle_swaps
        WHERE rental_agreement_number = '06761'
        ORDER BY swap_datetime DESC
    """)
    swaps = cur.fetchall()
    if swaps:
        for swap in swaps:
            print(f"   Swap #{swap[0]}: {swap[2]} → {swap[3]} at {swap[1]} by {swap[4]}")
    else:
        print("   ❌ No swaps found for RA 06761")
    
    # 8. CRITICAL: Check if there are OTHER RAs with 40-XM-45 that have active check-ins
    print("\n8️⃣ CRITICAL: Are there OTHER RAs with 40-XM-45 that might be blocking?")
    cur.execute("""
        SELECT DISTINCT vi.contract_number, vi.inspection_type, vi.status, vi.created_at
        FROM vehicle_inspections vi
        WHERE vi.vehicle_plate = '40-XM-45'
        AND vi.inspection_type = 'checkin'
        AND COALESCE(vi.status, '') != 'replaced'
        ORDER BY vi.created_at DESC
    """)
    other_checkins = cur.fetchall()
    if other_checkins:
        print("   ⚠️ YES - Found active check-ins for 40-XM-45:")
        for ci in other_checkins:
            print(f"      Contract: {ci[0]}, Type: {ci[1]}, Status: {ci[2] or 'NULL'}, Created: {ci[3]}")
            # Check if this contract has checkout
            ra_num = ci[0].split('-')[0] if '-' in ci[0] else ci[0]
            cur.execute("""
                SELECT inspection_number, inspection_type
                FROM vehicle_inspections
                WHERE contract_number LIKE %s
                AND inspection_type = 'checkout'
            """, (f"{ra_num}%",))
            checkout = cur.fetchone()
            if checkout:
                print(f"         ✅ Has checkout: {checkout[0]}")
            else:
                print(f"         ❌ NO CHECKOUT - This is blocking availability!")
    else:
        print("   ✅ NO - No active check-ins found for 40-XM-45")
    
    print("\n" + "=" * 100)
    print("🎯 CONCLUSION:")
    print("=" * 100)
    
    if not ras_with_40:
        print("✅ 40-XM-45 is NOT in rental_agreements.license_plate (good)")
    else:
        print("⚠️ 40-XM-45 IS in rental_agreements.license_plate (might block)")
    
    if other_checkins:
        print("❌ 40-XM-45 has ACTIVE check-ins without 'replaced' status (BLOCKING)")
        print("   → Need to mark these as 'replaced'")
    else:
        print("✅ 40-XM-45 has NO active check-ins (should be available)")
    
    if available:
        print("✅ 40-XM-45 PASSES the availability query")
    else:
        print("❌ 40-XM-45 FAILS the availability query")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
