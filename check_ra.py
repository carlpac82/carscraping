import psycopg2
import os
import json

DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Search for RA
cursor.execute("""
    SELECT rental_agreement_number, extracted_data 
    FROM rental_agreements 
    WHERE rental_agreement_number LIKE %s 
    OR rental_agreement_number LIKE %s
    LIMIT 5
""", ('%06716%', '%06716-09%'))

rows = cursor.fetchall()

print(f"Found {len(rows)} RAs:")
for row in rows:
    ra_number = row[0]
    extracted_data = row[1]
    print(f"\n📄 RA: {ra_number}")
    if extracted_data:
        try:
            data = json.loads(extracted_data)
            print(f"   Keys: {list(data.keys())}")
            print(f"   Client Email: {data.get('clientEmail', 'NOT FOUND')}")
        except:
            print(f"   Error parsing JSON")
    else:
        print(f"   No extracted_data")

conn.close()
