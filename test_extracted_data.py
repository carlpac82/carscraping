import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    database="carscrapingdb",
    user="postgres",
    password="Pacheco_1982"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT rental_agreement_number, license_plate, extracted_data 
    FROM rental_agreements 
    WHERE rental_agreement_number LIKE '06716%'
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    print(f"RA Number: {row[0]}")
    print(f"License Plate: {row[1]}")
    print(f"\nExtracted Data:")
    if row[2]:
        data = json.loads(row[2])
        print(json.dumps(data, indent=2))
        print(f"\n🔑 Keys available: {list(data.keys())}")
        print(f"\n👤 customer_name: {data.get('customer_name', 'NOT FOUND')}")
        print(f"👤 customerName: {data.get('customerName', 'NOT FOUND')}")
        print(f"📍 pickup_location: {data.get('pickup_location', 'NOT FOUND')}")
        print(f"📍 pickupLocation: {data.get('pickupLocation', 'NOT FOUND')}")
    else:
        print("No extracted data")
else:
    print("RA not found")

# Check inspections
cursor.execute("""
    SELECT id, inspection_type, contract_number, created_at
    FROM vehicle_inspections 
    WHERE contract_number LIKE '06716%'
    ORDER BY created_at DESC
""")

inspections = cursor.fetchall()
print(f"\n\n📋 Inspections found: {len(inspections)}")
for insp in inspections:
    print(f"  - ID: {insp[0]}, Type: {insp[1]}, Contract: {insp[2]}, Date: {insp[3]}")
    
    # Count photos for each inspection
    cursor.execute("""
        SELECT COUNT(*), array_agg(photo_type)
        FROM inspection_photos 
        WHERE inspection_id = %s AND photo_type != 'damage_croqui'
    """, (insp[0],))
    photo_info = cursor.fetchone()
    print(f"    Photos: {photo_info[0]} - Types: {photo_info[1]}")

conn.close()
