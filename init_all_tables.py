"""
Initialize ALL required tables for commissioners system
Run this script on Railway to create missing tables
"""

import os
import sys
from database import get_db
import logging

logging.basicConfig(level=logging.INFO)

def init_all_tables():
    """Create commissioners and bookings tables"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. Create commissioners table
        logging.info("📋 Creating commissioners table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commissioners (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                commission_rate DECIMAL(5, 2) DEFAULT 0.00,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("✅ Table 'commissioners' created successfully")
        
        # 2. Create bookings table
        logging.info("📋 Creating bookings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                customer_email VARCHAR(255) NOT NULL,
                customer_phone VARCHAR(50) NOT NULL,
                pickup_date DATE NOT NULL,
                return_date DATE NOT NULL,
                pickup_location VARCHAR(255) NOT NULL,
                return_location VARCHAR(255) NOT NULL,
                car_name VARCHAR(255) NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                commissioner_id INTEGER REFERENCES commissioners(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("✅ Table 'bookings' created successfully")
        
        # 3. Create indexes
        logging.info("📋 Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_commissioner 
            ON bookings(commissioner_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_status 
            ON bookings(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_dates 
            ON bookings(pickup_date, return_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_created 
            ON bookings(created_at DESC)
        """)
        logging.info("✅ Indexes created successfully")
        
        # 4. Create trigger functions
        logging.info("📋 Creating trigger functions...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # 5. Create triggers
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_commissioners_updated_at ON commissioners
        """)
        cursor.execute("""
            CREATE TRIGGER update_commissioners_updated_at 
            BEFORE UPDATE ON commissioners
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings
        """)
        cursor.execute("""
            CREATE TRIGGER update_bookings_updated_at 
            BEFORE UPDATE ON bookings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        logging.info("✅ Triggers created successfully")
        
        conn.commit()
        logging.info("🎉 ALL TABLES INITIALIZED SUCCESSFULLY!")
        logging.info("")
        logging.info("📊 Tables created:")
        logging.info("   ✓ commissioners")
        logging.info("   ✓ bookings")
        logging.info("")
        logging.info("🔍 Verify tables exist:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name IN ('commissioners', 'bookings')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            logging.info(f"   ✓ {table[0]}")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_all_tables()
