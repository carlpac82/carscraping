#!/usr/bin/env python3
"""
Script para criar tabela de emails de checkout agendados
"""

import os
import sys

def create_scheduled_emails_table():
    """Cria tabela scheduled_checkout_emails na base de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False
        
        import psycopg2
        
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📋 Creating scheduled_checkout_emails table...")
        
        # Criar tabela
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_checkout_emails (
                id SERIAL PRIMARY KEY,
                inspection_number VARCHAR(100) NOT NULL UNIQUE,
                checkout_date DATE NOT NULL,
                scheduled_send_date TIMESTAMP NOT NULL,
                pickup_location VARCHAR(255) NOT NULL,
                client_email VARCHAR(255) NOT NULL,
                client_name VARCHAR(255),
                vehicle_plate VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                error_message TEXT,
                CONSTRAINT valid_status CHECK (status IN ('pending', 'sent', 'cancelled', 'error'))
            )
        """)
        
        print("📊 Creating indexes...")
        
        # Criar índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_emails_send_date 
            ON scheduled_checkout_emails(scheduled_send_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_emails_status 
            ON scheduled_checkout_emails(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_emails_inspection 
            ON scheduled_checkout_emails(inspection_number)
        """)
        
        conn.commit()
        
        print("✅ Table and indexes created successfully!")
        
        # Verificar
        cursor.execute("""
            SELECT COUNT(*) FROM scheduled_checkout_emails
        """)
        count = cursor.fetchone()[0]
        print(f"📊 Current records in table: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 SETUP SCHEDULED CHECKOUT EMAILS TABLE")
    print("="*80 + "\n")
    
    success = create_scheduled_emails_table()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)
