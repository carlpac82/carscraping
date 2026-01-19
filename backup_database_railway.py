#!/usr/bin/env python3
"""
Backup PostgreSQL database from Railway
"""
import os
import subprocess
import sys
from datetime import datetime

def backup_railway_database():
    """Backup PostgreSQL database from Railway"""
    
    # Get DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("ℹ️  Please set DATABASE_URL from Railway dashboard")
        print("ℹ️  Example: export DATABASE_URL='postgresql://...'")
        return False
    
    # Create backup directory
    backup_dir = "backups/database"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/railway_postgres_{timestamp}.sql"
    
    print(f"🔄 Starting PostgreSQL backup from Railway...")
    print(f"📦 Output file: {backup_file}")
    
    try:
        # Run pg_dump
        result = subprocess.run(
            ['pg_dump', database_url],
            stdout=open(backup_file, 'w'),
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            # Get file size
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            print(f"✅ Database backup completed successfully!")
            print(f"📊 Backup size: {size_mb:.2f} MB")
            print(f"📁 Location: {backup_file}")
            return True
        else:
            print(f"❌ pg_dump failed with error:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ pg_dump command not found")
        print("ℹ️  Please install PostgreSQL client tools:")
        print("   brew install postgresql")
        return False
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        return False

if __name__ == "__main__":
    success = backup_railway_database()
    sys.exit(0 if success else 1)
