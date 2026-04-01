#!/usr/bin/env python3
"""
Migration script for commission payment tracking
Adds columns for commission payment status and user permissions
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

def migrate_commission_payment():
    """Add commission payment columns to database"""
    conn = get_db()
    cursor = conn.cursor()
    
    print("🔄 Starting commission payment migration...")
    
    results = []
    
    # Add commission_paid column
    try:
        cursor.execute("ALTER TABLE commission_bookings ADD COLUMN commission_paid BOOLEAN DEFAULT FALSE")
        conn.commit()
        results.append("✅ commission_paid: CREATED")
        print("✅ Added commission_paid column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            results.append("ℹ️ commission_paid: ALREADY EXISTS")
            print("ℹ️ commission_paid column already exists")
        else:
            results.append(f"❌ commission_paid: ERROR - {e}")
            print(f"❌ Error adding commission_paid: {e}")
    
    # Add commission_paid_date column
    try:
        cursor.execute("ALTER TABLE commission_bookings ADD COLUMN commission_paid_date TIMESTAMP")
        conn.commit()
        results.append("✅ commission_paid_date: CREATED")
        print("✅ Added commission_paid_date column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            results.append("ℹ️ commission_paid_date: ALREADY EXISTS")
            print("ℹ️ commission_paid_date column already exists")
        else:
            results.append(f"❌ commission_paid_date: ERROR - {e}")
            print(f"❌ Error adding commission_paid_date: {e}")
    
    # Add commission_paid_by column
    try:
        cursor.execute("ALTER TABLE commission_bookings ADD COLUMN commission_paid_by INTEGER")
        conn.commit()
        results.append("✅ commission_paid_by: CREATED")
        print("✅ Added commission_paid_by column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            results.append("ℹ️ commission_paid_by: ALREADY EXISTS")
            print("ℹ️ commission_paid_by column already exists")
        else:
            results.append(f"❌ commission_paid_by: ERROR - {e}")
            print(f"❌ Error adding commission_paid_by: {e}")
    
    # Add can_manage_commissions to users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN can_manage_commissions INTEGER DEFAULT 0")
        conn.commit()
        results.append("✅ can_manage_commissions: CREATED")
        print("✅ Added can_manage_commissions column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            results.append("ℹ️ can_manage_commissions: ALREADY EXISTS")
            print("ℹ️ can_manage_commissions column already exists")
        else:
            results.append(f"❌ can_manage_commissions: ERROR - {e}")
            print(f"❌ Error adding can_manage_commissions: {e}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("MIGRATION SUMMARY:")
    for result in results:
        print(f"  {result}")
    print("="*50)
    
    return results

if __name__ == "__main__":
    try:
        migrate_commission_payment()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
