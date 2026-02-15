#!/usr/bin/env python3
"""Script to fix plate BA-28-FP -> BI-78-FM for RA 06829"""

import sys
import os

# Add parent directory to path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import _db_connect, _USE_NEW_DB
import json

def fix_plate():
    conn = _db_connect()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("FIXING PLATE FOR RA 06829: BA-28-FP -> BI-78-FM")
    print("=" * 60)
    
    # Check current inspections
    print("\n📋 BEFORE UPDATE - Inspections:")
    if _USE_NEW_DB:
        cursor.execute("""
            SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
            FROM vehicle_inspections 
            WHERE contract_number LIKE %s AND vehicle_plate = %s
        """, ('06829%', 'BA-28-FP'))
    else:
        cursor.execute("""
            SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
            FROM vehicle_inspections 
            WHERE contract_number LIKE ? AND vehicle_plate = ?
        """, ('06829%', 'BA-28-FP'))
    
    inspections = cursor.fetchall()
    if inspections:
        for insp in inspections:
            print(f"  - {insp[0]} | {insp[1]} | {insp[2]} | {insp[3]}")
    else:
        print("  No inspections found with BA-28-FP")
    
    # Check rental agreement
    print("\n📄 BEFORE UPDATE - Rental Agreement:")
    if _USE_NEW_DB:
        cursor.execute("""
            SELECT rental_agreement_number, license_plate, extracted_data 
            FROM rental_agreements 
            WHERE rental_agreement_number LIKE %s
        """, ('06829%',))
    else:
        cursor.execute("""
            SELECT rental_agreement_number, license_plate, extracted_data 
            FROM rental_agreements 
            WHERE rental_agreement_number LIKE ?
        """, ('06829%',))
    
    ra = cursor.fetchone()
    if ra:
        print(f"  - RA: {ra[0]} | Plate: {ra[1]}")
    else:
        print("  No rental agreement found")
    
    # Update inspections
    print("\n🔧 UPDATING INSPECTIONS...")
    if _USE_NEW_DB:
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET vehicle_plate = %s 
            WHERE contract_number LIKE %s AND vehicle_plate = %s
        """, ('BI-78-FM', '06829%', 'BA-28-FP'))
    else:
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET vehicle_plate = ? 
            WHERE contract_number LIKE ? AND vehicle_plate = ?
        """, ('BI-78-FM', '06829%', 'BA-28-FP'))
    
    insp_count = cursor.rowcount
    print(f"  ✅ Updated {insp_count} inspection(s)")
    
    # Update rental agreement plate
    print("\n🔧 UPDATING RENTAL AGREEMENT...")
    if _USE_NEW_DB:
        cursor.execute("""
            UPDATE rental_agreements 
            SET license_plate = %s 
            WHERE rental_agreement_number LIKE %s
        """, ('BI-78-FM', '06829%'))
    else:
        cursor.execute("""
            UPDATE rental_agreements 
            SET license_plate = ? 
            WHERE rental_agreement_number LIKE ?
        """, ('BI-78-FM', '06829%'))
    
    ra_count = cursor.rowcount
    print(f"  ✅ Updated {ra_count} rental agreement(s)")
    
    # Update extracted_data JSON
    if ra and ra[2]:
        print("\n🔧 UPDATING EXTRACTED_DATA JSON...")
        try:
            extracted = json.loads(ra[2]) if isinstance(ra[2], str) else ra[2]
            if 'plate' in extracted:
                old_plate = extracted['plate']
                extracted['plate'] = 'BI-78-FM'
                
                if _USE_NEW_DB:
                    cursor.execute("""
                        UPDATE rental_agreements 
                        SET extracted_data = %s 
                        WHERE rental_agreement_number LIKE %s
                    """, (json.dumps(extracted), '06829%'))
                else:
                    cursor.execute("""
                        UPDATE rental_agreements 
                        SET extracted_data = ? 
                        WHERE rental_agreement_number LIKE ?
                    """, (json.dumps(extracted), '06829%'))
                
                print(f"  ✅ Updated extracted_data: {old_plate} -> BI-78-FM")
        except Exception as e:
            print(f"  ⚠️ Could not update extracted_data: {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify changes
    print("\n" + "=" * 60)
    print("VERIFICATION - AFTER UPDATE")
    print("=" * 60)
    
    print("\n📋 Inspections:")
    if _USE_NEW_DB:
        cursor.execute("""
            SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
            FROM vehicle_inspections 
            WHERE contract_number LIKE %s
        """, ('06829%',))
    else:
        cursor.execute("""
            SELECT inspection_number, vehicle_plate, contract_number, inspection_type 
            FROM vehicle_inspections 
            WHERE contract_number LIKE ?
        """, ('06829%',))
    
    inspections = cursor.fetchall()
    if inspections:
        for insp in inspections:
            print(f"  - {insp[0]} | {insp[1]} | {insp[2]} | {insp[3]}")
    else:
        print("  No inspections found")
    
    print("\n📄 Rental Agreement:")
    if _USE_NEW_DB:
        cursor.execute("""
            SELECT rental_agreement_number, license_plate 
            FROM rental_agreements 
            WHERE rental_agreement_number LIKE %s
        """, ('06829%',))
    else:
        cursor.execute("""
            SELECT rental_agreement_number, license_plate 
            FROM rental_agreements 
            WHERE rental_agreement_number LIKE ?
        """, ('06829%',))
    
    ra = cursor.fetchone()
    if ra:
        print(f"  - RA: {ra[0]} | Plate: {ra[1]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ DONE! Plate updated: BA-28-FP -> BI-78-FM")
    print("=" * 60)

if __name__ == '__main__':
    fix_plate()
