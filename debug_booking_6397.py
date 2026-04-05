import sqlite3
import os

def debug_booking_6397():
    """Debug booking 6397 to check language field"""
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        print("🔍 Debugging booking 6397...")
        print("=" * 50)
        
        # Get the booking with all fields
        cur.execute("""
            SELECT 
                cb.id,
                cb.voucher_number,
                cb.client_name,
                cb.client_email,
                cb.client_phone,
                cb.hotel,
                cb.room_number,
                cb.pickup_date,
                cb.pickup_time,
                cb.dropoff_date,
                cb.dropoff_time,
                cb.pickup_location,
                cb.dropoff_location,
                cb.vehicle_group,
                cb.extras,
                cb.flight_number,
                cb.language,
                cb.observations,
                cb.deposit,
                cb.price,
                cb.created_at,
                c.name as agent_name,
                c.email as agent_email,
                c.phone as agent_phone
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE cb.id = 6397
        """)
        
        result = cur.fetchone()
        
        if not result:
            print("❌ Booking 6397 not found")
            return
        
        print(f"📋 Booking ID: {result[0]}")
        print(f"🎫 Voucher: {result[1]}")
        print(f"👤 Client: {result[2]}")
        print(f"📧 Email: {result[3]}")
        print(f"📱 Phone: {result[4]}")
        print(f"🏨 Hotel: {result[5]}")
        print(f"🚪 Room: {result[6]}")
        print(f"📅 Pickup Date: {result[7]}")
        print(f"⏰ Pickup Time: {result[8]}")
        print(f"📅 Dropoff Date: {result[9]}")
        print(f"⏰ Dropoff Time: {result[10]}")
        print(f"📍 Pickup Location: {result[11]}")
        print(f"📍 Dropoff Location: {result[12]}")
        print(f"🚗 Vehicle Group: {result[13]}")
        print(f"📦 Extras: {result[14]}")
        print(f"✈️ Flight Number: {result[15]}")
        print(f"🌐 LANGUAGE: '{result[16]}'")
        print(f"📝 Observations: {result[17]}")
        print(f"💰 Deposit: {result[18]}")
        print(f"💵 Price: {result[19]}")
        print(f"📅 Created At: {result[20]}")
        print(f"👨‍💼 Agent Name: {result[21]}")
        print(f"📧 Agent Email: {result[22]}")
        print(f"📱 Agent Phone: {result[23]}")
        
        print("=" * 50)
        print(f"🎯 LANGUAGE FIELD ANALYSIS:")
        print(f"   - Raw value: '{result[16]}'")
        print(f"   - Type: {type(result[16])}")
        print(f"   - Is None: {result[16] is None}")
        print(f"   - Is empty string: {result[16] == ''}")
        print(f"   - Lower case: '{result[16].lower() if result[16] else 'None'}'")
        
        # Check template files
        print("=" * 50)
        print(f"📄 TEMPLATE FILES CHECK:")
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        templates = {
            'pt': 'voucher_template_pt.html',
            'en': 'voucher_template_en.html',
            'fr': 'voucher_template_fr.html',
            'es': 'voucher_template_es.html',
            'de': 'voucher_template_de.html'
        }
        
        for lang, template in templates.items():
            template_path = os.path.join(templates_dir, template)
            exists = os.path.exists(template_path)
            print(f"   - {lang}: {template} {'✅' if exists else '❌'}")
        
        # Test language mapping
        print("=" * 50)
        print(f"🌐 LANGUAGE MAPPING TEST:")
        language = result[16] or 'pt'
        language = language.lower()
        
        language_templates = {
            'pt': 'voucher_template_pt.html',
            'en': 'voucher_template_en.html', 
            'fr': 'voucher_template_fr.html',
            'es': 'voucher_template_es.html',
            'de': 'voucher_template_de.html'
        }
        
        template_file = language_templates.get(language, 'voucher_template_pt.html')
        print(f"   - Input language: '{result[16]}'")
        print(f"   - Normalized: '{language}'")
        print(f"   - Selected template: '{template_file}'")
        
        template_path = os.path.join(templates_dir, template_file)
        print(f"   - Full path: '{template_path}'")
        print(f"   - Exists: {os.path.exists(template_path)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_booking_6397()
