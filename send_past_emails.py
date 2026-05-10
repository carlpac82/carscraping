import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Buscar todos os emails pendentes
cursor.execute("""
    SELECT inspection_number, checkout_date, scheduled_send_date,
           pickup_location, client_email, client_name, vehicle_plate
    FROM scheduled_checkout_emails
    WHERE status = 'pending'
    ORDER BY scheduled_send_date ASC
""")
rows = cursor.fetchall()

print(f"Found {len(rows)} pending email(s)")

for row in rows:
    inspection_number, checkout_date, scheduled_send_date, pickup_location, client_email, client_name, vehicle_plate = row
    print(f"Processing {inspection_number} - {client_email}")
    
    # Importar funções
    from schedule_checkout_emails import mark_email_sent
    from main import _send_self_checkout_email
    
    try:
        success = _send_self_checkout_email(
            inspection_number=inspection_number,
            checkout_date=checkout_date,
            pickup_location=pickup_location,
            client_email=client_email,
            client_name=client_name,
            vehicle_plate=vehicle_plate
        )
        
        if success:
            mark_email_sent(inspection_number, success=True)
            print(f"✅ Sent: {inspection_number}")
        else:
            mark_email_sent(inspection_number, success=False, error_message="Failed")
            print(f"❌ Failed: {inspection_number}")
    except Exception as e:
        mark_email_sent(inspection_number, success=False, error_message=str(e))
        print(f"❌ Error: {inspection_number} - {e}")

conn.commit()
conn.close()
print("Done!")
