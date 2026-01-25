#!/usr/bin/env python3
"""
Script temporário para criar tabela via endpoint HTTP
"""

import requests
import os

# URL do Railway
BASE_URL = "https://carscraping-production.up.railway.app"

# Criar endpoint temporário para executar setup
setup_code = """
import os
import psycopg2

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Criar tabela
cursor.execute('''
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
''')

# Criar índices
cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_emails_send_date ON scheduled_checkout_emails(scheduled_send_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_emails_status ON scheduled_checkout_emails(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_emails_inspection ON scheduled_checkout_emails(inspection_number)')

conn.commit()
cursor.close()
conn.close()

print("✅ Table created successfully!")
"""

print(setup_code)
