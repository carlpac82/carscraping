#!/usr/bin/env python3
"""
Script para criar tabela broker_bookings
"""
import os
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    """Obter DATABASE_URL do ficheiro .env"""
    database_url = None
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    
    return database_url

def create_broker_bookings_table():
    """Criar tabela broker_bookings"""
    print("=" * 80)
    print("CRIANDO TABELA BROKER_BOOKINGS")
    print("=" * 80)
    
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    result = urlparse(database_url)
    
    try:
        conn = psycopg2.connect(
            database="railway",
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        print("✅ Conectado à base de dados")
        
        # Verificar se tabela já existe
        cursor.execute('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'broker_bookings'
            )
        ''')
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("⚠ Tabela broker_bookings já existe")
            cursor.execute('SELECT COUNT(*) FROM broker_bookings')
            count = cursor.fetchone()[0]
            print(f"📊 Registros existentes: {count}")
        else:
            # Criar tabela
            create_table_sql = '''
                CREATE TABLE broker_bookings (
                    id SERIAL PRIMARY KEY,
                    broker_name VARCHAR(255) NOT NULL,
                    voucher_number VARCHAR(100) NOT NULL,
                    client_name VARCHAR(255),
                    pickup_date DATE NOT NULL,
                    dropoff_date DATE,
                    vehicle_group VARCHAR(100),
                    days INTEGER,
                    total_price DECIMAL(10,2),
                    status VARCHAR(50) DEFAULT 'confirmed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
            
            cursor.execute(create_table_sql)
            
            # Criar índices
            cursor.execute('CREATE INDEX idx_broker_bookings_broker ON broker_bookings(broker_name)')
            cursor.execute('CREATE INDEX idx_broker_bookings_voucher ON broker_bookings(voucher_number)')
            cursor.execute('CREATE INDEX idx_broker_bookings_date ON broker_bookings(pickup_date)')
            
            # Criar trigger para updated_at
            cursor.execute('''
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            ''')
            
            cursor.execute('''
                CREATE TRIGGER update_broker_bookings_updated_at 
                BEFORE UPDATE ON broker_bookings 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            ''')
            
            conn.commit()
            print("✅ Tabela broker_bookings criada com sucesso")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    create_broker_bookings_table()
