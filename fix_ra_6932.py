import psycopg2
import os
from datetime import datetime

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()

try:
    # Get swap data
    cur.execute("""
        SELECT old_kms, old_fuel, new_kms, new_fuel
        FROM vehicle_swaps
        WHERE rental_agreement_number = '6932'
          AND old_plate = 'AS-78-RH'
          AND new_plate = 'AT-28-NX'
        ORDER BY swap_datetime DESC
        LIMIT 1
    """)
    
    swap_data = cur.fetchone()
    if swap_data:
        print(f"✅ Found swap: old_kms={swap_data[0]}, old_fuel={swap_data[1]}, new_kms={swap_data[2]}, new_fuel={swap_data[3]}")
        new_kms = swap_data[2]
        new_fuel = swap_data[3]
    else:
        print("⚠️ No swap found, using default values")
        new_kms = 0
        new_fuel = 'N/A'
    
    # Get old inspection
    cur.execute("""
        SELECT id, inspection_number, vehicle_brand, vehicle_model, customer_name, 
               customer_email, customer_phone, inspector_name, inspector_notes,
               has_damage, damage_count, damage_severity, ai_analysis_complete,
               ai_confidence_avg, ai_damages_detected, fuel_level
        FROM vehicle_inspections
        WHERE contract_number LIKE '6932%'
          AND vehicle_plate = 'AS-78-RH'
          AND inspection_type = 'checkin'
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    old_inspection = cur.fetchone()
    
    if not old_inspection:
        print("❌ No old inspection found for AS-78-RH")
        exit(1)
    
    old_inspection_id = old_inspection[0]
    print(f"✅ Found old inspection ID: {old_inspection_id} ({old_inspection[1]})")
    
    # Check if new inspection already exists
    cur.execute("""
        SELECT id FROM vehicle_inspections
        WHERE contract_number LIKE '6932%'
          AND vehicle_plate = 'AT-28-NX'
          AND inspection_type = 'checkin'
    """)
    
    existing = cur.fetchone()
    if existing:
        print(f"⚠️ New inspection already exists (ID: {existing[0]}), skipping creation")
    else:
        # Generate new inspection number
        now = datetime.now()
        new_inspection_number = f"VI-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
        
        # Count photos
        cur.execute("SELECT COUNT(*) FROM inspection_photos WHERE inspection_id = %s", (old_inspection_id,))
        photo_count = cur.fetchone()[0]
        
        print(f"📋 Creating new inspection for AT-28-NX...")
        
        # Create new inspection
        cur.execute("""
            INSERT INTO vehicle_inspections 
            (inspection_number, inspection_type, vehicle_plate, vehicle_brand, vehicle_model,
             contract_number, customer_name, customer_email, customer_phone,
             inspector_name, inspector_notes, has_damage, damage_count, damage_severity,
             ai_analysis_complete, ai_confidence_avg, ai_damages_detected,
             odometer_reading, fuel_level, status, photo_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            new_inspection_number,
            'checkin',
            'AT-28-NX',
            old_inspection[2],  # vehicle_brand
            old_inspection[3],  # vehicle_model
            '6932',
            old_inspection[4],  # customer_name
            old_inspection[5],  # customer_email
            old_inspection[6],  # customer_phone
            old_inspection[7],  # inspector_name
            old_inspection[8],  # inspector_notes
            old_inspection[9],  # has_damage
            old_inspection[10], # damage_count
            old_inspection[11], # damage_severity
            old_inspection[12], # ai_analysis_complete
            old_inspection[13], # ai_confidence_avg
            old_inspection[14], # ai_damages_detected
            new_kms,
            new_fuel,
            'completed',
            photo_count
        ))
        
        new_inspection_id = cur.fetchone()[0]
        print(f"✅ Created new inspection ID: {new_inspection_id} ({new_inspection_number})")
        
        # Copy photos
        cur.execute("""
            INSERT INTO inspection_photos
            (inspection_id, photo_type, photo_order, image_data, image_filename,
             image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type,
             ai_confidence, ai_result)
            SELECT %s, photo_type, photo_order, image_data, image_filename,
                   image_size, image_format, ai_analyzed, ai_has_damage, ai_damage_type,
                   ai_confidence, ai_result
            FROM inspection_photos
            WHERE inspection_id = %s
        """, (new_inspection_id, old_inspection_id))
        
        photos_copied = cur.rowcount
        print(f"✅ Copied {photos_copied} photo(s)")
        
        # Copy damages
        cur.execute("SELECT COUNT(*) FROM inspection_damages WHERE inspection_id = %s", (old_inspection_id,))
        damage_count = cur.fetchone()[0]
        
        if damage_count > 0:
            cur.execute("""
                INSERT INTO inspection_damages
                (inspection_id, damage_type, damage_position_x, damage_position_y,
                 damage_description, damage_severity, photo_reference)
                SELECT %s, damage_type, damage_position_x, damage_position_y,
                       damage_description, damage_severity, photo_reference
                FROM inspection_damages
                WHERE inspection_id = %s
            """, (new_inspection_id, old_inspection_id))
            
            damages_copied = cur.rowcount
            print(f"✅ Copied {damages_copied} damage(s)")
        
        conn.commit()
        print("\n✅ RA 6932 fixed successfully! You can now checkout AT-28-NX")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    cur.close()
    conn.close()
