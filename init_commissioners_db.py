"""
Initialize Commissioners Database Tables
Creates tables for commission booking system
"""

import os
import sys
from database import get_db
import logging

logging.basicConfig(level=logging.INFO)

def init_commissioners_tables():
    """Create commissioners and commission_bookings tables"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Create commissioners table
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
        
        # Create commission_bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commission_bookings (
                id SERIAL PRIMARY KEY,
                commissioner_id INTEGER NOT NULL REFERENCES commissioners(id),
                voucher_number VARCHAR(50) NOT NULL UNIQUE,
                
                client_name VARCHAR(255) NOT NULL,
                client_email VARCHAR(255) NOT NULL,
                client_phone VARCHAR(50) NOT NULL,
                
                pickup_date DATE NOT NULL,
                pickup_time TIME NOT NULL,
                dropoff_date DATE NOT NULL,
                dropoff_time TIME NOT NULL,
                pickup_location TEXT NOT NULL,
                dropoff_location TEXT NOT NULL,
                
                vehicle_group VARCHAR(10) NOT NULL,
                extras JSONB DEFAULT '[]',
                
                flight_number VARCHAR(50),
                language VARCHAR(5) NOT NULL DEFAULT 'pt',
                observations TEXT,
                price DECIMAL(10, 2) NOT NULL,
                
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("✅ Table 'commission_bookings' created successfully")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_commissioner_bookings 
            ON commission_bookings(commissioner_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_booking_dates 
            ON commission_bookings(pickup_date, dropoff_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_voucher_number 
            ON commission_bookings(voucher_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_booking_status 
            ON commission_bookings(status)
        """)
        logging.info("✅ Indexes created successfully")
        
        # Create trigger function for updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # Create triggers
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_commissioners_updated_at ON commissioners
        """)
        cursor.execute("""
            CREATE TRIGGER update_commissioners_updated_at 
            BEFORE UPDATE ON commissioners
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_commission_bookings_updated_at ON commission_bookings
        """)
        cursor.execute("""
            CREATE TRIGGER update_commission_bookings_updated_at 
            BEFORE UPDATE ON commission_bookings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        logging.info("✅ Triggers created successfully")
        
        conn.commit()
        logging.info("🎉 All commissioners tables initialized successfully!")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Error creating tables: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_commissioners_tables()
