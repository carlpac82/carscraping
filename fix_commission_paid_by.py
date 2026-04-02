#!/usr/bin/env python3
"""
Migration script to fix commission_paid_by column type from INTEGER to TEXT
"""

import psycopg2
import os
import sys

def migrate_commission_paid_by_column():
    """Change commission_paid_by column from INTEGER to TEXT"""
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        print("💡 Obter do Render/Railway Dashboard")
        return False
    
    # Fix for Railway/Render that use postgres:// instead of postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if column exists and its type
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name = 'commission_paid_by'
        """)
        column_info = cursor.fetchone()
        
        if not column_info:
            print("❌ Column commission_paid_by not found")
            return False
        
        print(f"📋 Current column info: {column_info}")
        
        # PostgreSQL supports ALTER COLUMN TYPE
        print("🔄 Altering column type from INTEGER to TEXT...")
        
        cursor.execute("""
            ALTER TABLE commission_bookings 
            ALTER COLUMN commission_paid_by TYPE TEXT
        """)
        
        conn.commit()
        print("✅ Successfully altered commission_paid_by column to TEXT")
        
        # Verify the change
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'commission_bookings' 
            AND column_name = 'commission_paid_by'
        """)
        new_column_info = cursor.fetchone()
        
        print(f"✅ New column info: {new_column_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting migration of commission_paid_by column...")
    success = migrate_commission_paid_by_column()
    
    if success:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)
