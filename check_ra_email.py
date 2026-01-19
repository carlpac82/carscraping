#!/usr/bin/env python3
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", 5432)),
    database=os.getenv("POSTGRES_DB", "carscraping"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "")
)

cursor = conn.cursor()

# Query RA 06716
ra_number = "06716"
cursor.execute("""
    SELECT rental_agreement_number, extracted_data 
    FROM rental_agreements 
    WHERE rental_agreement_number LIKE %s
""", (f"%{ra_number}%",))

rows = cursor.fetchall()

print(f"\n🔍 Found {len(rows)} RAs matching '{ra_number}':\n")

for row in rows:
    ra_num = row[0]
    extracted_data = row[1]
    
    print(f"📄 RA: {ra_num}")
    
    if extracted_data:
        try:
            data = json.loads(extracted_data)
            print(f"   📧 clientEmail: {data.get('clientEmail', 'NOT FOUND')}")
            print(f"   👤 clientName: {data.get('clientName', 'NOT FOUND')}")
            print(f"   📞 clientPhone: {data.get('clientPhone', 'NOT FOUND')}")
            print(f"\n   Full extracted_data keys: {list(data.keys())}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Error parsing JSON: {e}")
    else:
        print(f"   ⚠️ No extracted_data found")
    
    print()

cursor.close()
conn.close()
