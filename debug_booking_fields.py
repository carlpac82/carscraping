import sqlite3
import os

def debug_booking_fields():
    """Debug booking fields to find language field"""
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Get table schema
        print("📋 Commission Bookings Table Schema:")
        cur.execute("PRAGMA table_info(commission_bookings)")
        columns = cur.fetchall()
        
        print("\n📊 Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Get a sample booking
        print("\n🔍 Sample booking data:")
        cur.execute("SELECT * FROM commission_bookings LIMIT 1")
        booking = cur.fetchone()
        
        if booking:
            print(f"Total columns: {len(booking)}")
            for i, value in enumerate(booking):
                print(f"  Column {i}: {value}")
        
        # Look for language-related fields
        print("\n🌐 Looking for language-related fields:")
        for col in columns:
            col_name = col[1].lower()
            if 'lang' in col_name or 'idioma' in col_name or 'language' in col_name:
                print(f"  🎯 Found potential language field: {col[1]}")
        
        # Get all unique values for potential language fields
        print("\n🔍 Checking for language patterns in data:")
        cur.execute("SELECT * FROM commission_bookings LIMIT 10")
        bookings = cur.fetchall()
        
        for booking in bookings:
            for i, value in enumerate(booking):
                if value and isinstance(value, str):
                    if value.lower() in ['pt', 'en', 'fr', 'es', 'de', 'portugues', 'ingles', 'frances', 'espanhol', 'alemao']:
                        print(f"  🌐 Found language value: '{value}' at column {i}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_booking_fields()
