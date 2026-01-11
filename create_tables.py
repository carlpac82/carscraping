#!/usr/bin/env python3
import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

print("🔄 Criando tabelas PostgreSQL...")
print("")

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Tabela users
    print("📝 Criando tabela users...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          first_name TEXT,
          last_name TEXT,
          mobile TEXT,
          email TEXT,
          profile_picture_path TEXT,
          profile_picture_data BYTEA,
          is_admin INTEGER DEFAULT 0,
          enabled INTEGER DEFAULT 1,
          created_at TEXT,
          google_id TEXT UNIQUE,
          role TEXT DEFAULT 'user',
          can_access_inspection INTEGER DEFAULT 0
        )
    """)
    print("✅ Tabela users criada")
    
    # Inserir utilizadores
    print("👥 Criando utilizadores padrão...")
    cursor.execute("""
        INSERT INTO users (username, password_hash, first_name, last_name, is_admin, enabled)
        VALUES 
          ('admin', 'scrypt:32768:8:1$yqVZ0M3sPEplemena$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'Admin', 'User', 1, 1),
          ('carlpac82', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'Carlos', 'Pacheco', 1, 1),
          ('dprudente', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'D', 'Prudente', 0, 1),
          ('LP', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'LP', 'User', 0, 1)
        ON CONFLICT (username) DO NOTHING
    """)
    print("✅ Utilizadores criados")
    
    # Tabela system_logs
    print("📝 Criando tabela system_logs...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
          id SERIAL PRIMARY KEY,
          timestamp TEXT NOT NULL,
          level TEXT NOT NULL,
          message TEXT NOT NULL,
          module TEXT,
          function TEXT,
          line_number INTEGER,
          exception TEXT
        )
    """)
    print("✅ Tabela system_logs criada")
    
    # Tabela recent_searches
    print("📝 Criando tabela recent_searches...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recent_searches (
          id SERIAL PRIMARY KEY,
          "user" TEXT NOT NULL,
          pickup_location TEXT NOT NULL,
          dropoff_location TEXT,
          pickup_date TEXT NOT NULL,
          dropoff_date TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          source TEXT DEFAULT 'manual',
          username TEXT
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recent_searches_user 
        ON recent_searches("user", created_at DESC)
    """)
    print("✅ Tabela recent_searches criada")
    
    # Tabela whatsapp_config
    print("📝 Criando tabela whatsapp_config...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_config (
          id SERIAL PRIMARY KEY,
          access_token TEXT,
          phone_number_id TEXT,
          business_account_id TEXT,
          verify_token TEXT,
          token_expires_at TIMESTAMP
        )
    """)
    print("✅ Tabela whatsapp_config criada")
    
    cursor.close()
    conn.close()
    
    print("")
    print("✅ Todas as tabelas criadas com sucesso!")
    print("")
    print("Próximo passo:")
    print("1. Ir para Railway > carscraping service")
    print("2. Deployments tab > ⋮ > Redeploy")
    print("3. Aguardar deploy completar")
    print("4. App deve iniciar sem erros!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
