#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    exit(1)

# Parse the URL
url = urlparse(database_url)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    user=url.username,
    password=url.password,
    database=url.path[1:]
)

cur = conn.cursor()

print("\n" + "="*80)
print("🔍 CHECKING STATE OF VEHICLE 40-XM-45")
print("="*80)

# Check vehicle_swaps
print("\n1️⃣ VEHICLE SWAPS:")
cur.execute("""
    SELECT rental_agreement_number, swap_datetime, old_plate, new_plate, employee_name
    FROM vehicle_swaps
    WHERE old_plate = '40-XM-45' OR new_plate = '40-XM-45'
    ORDER BY swap_datetime DESC
    LIMIT 5
""")
swaps = cur.fetchall()
if swaps:
    for swap in swaps:
        print(f"  RA: {swap[0]}, Date: {swap[1]}, {swap[2]} → {swap[3]}, By: {swap[4]}")
else:
    print("  ✅ No swaps found")

# Check vehicle_inspections
print("\n2️⃣ VEHICLE INSPECTIONS:")
cur.execute("""
    SELECT inspection_number, contract_number, inspection_type, status, created_at
    FROM vehicle_inspections
    WHERE vehicle_plate = '40-XM-45'
    ORDER BY created_at DESC
    LIMIT 5
""")
inspections = cur.fetchall()
if inspections:
    for insp in inspections:
        print(f"  #{insp[0]}: RA={insp[1]}, Type={insp[2]}, Status={insp[3]}, Date={insp[4]}")
else:
    print("  ✅ No inspections found")

# Check rental_agreements
print("\n3️⃣ RENTAL AGREEMENTS:")
cur.execute("""
    SELECT rental_agreement_number, license_plate, client_name, created_at
    FROM rental_agreements
    WHERE license_plate = '40-XM-45'
    ORDER BY created_at DESC
    LIMIT 5
""")
ras = cur.fetchall()
if ras:
    for ra in ras:
        print(f"  RA: {ra[0]}, Plate: {ra[1]}, Client: {ra[2]}, Date: {ra[3]}")
else:
    print("  ✅ No rental agreements found")

# Check vehicles table
print("\n4️⃣ VEHICLES TABLE:")
cur.execute("""
    SELECT matricula, status, km_atual, nivel_combustivel
    FROM vehicles
    WHERE matricula = '40-XM-45'
""")
vehicle = cur.fetchone()
if vehicle:
    print(f"  Plate: {vehicle[0]}, Status: {vehicle[1]}, KM: {vehicle[2]}, Fuel: {vehicle[3]}%")
else:
    print("  ⚠️ Vehicle not found in vehicles table")

print("\n" + "="*80)
print("✅ CHECK COMPLETE")
print("="*80 + "\n")

cur.close()
conn.close()
