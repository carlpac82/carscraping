-- Script para criar todas as tabelas PostgreSQL
-- Executar este SQL diretamente na base de dados Railway

-- Tabela users
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
);

-- Tabela system_logs
CREATE TABLE IF NOT EXISTS system_logs (
  id SERIAL PRIMARY KEY,
  timestamp TEXT NOT NULL,
  level TEXT NOT NULL,
  message TEXT NOT NULL,
  module TEXT,
  function TEXT,
  line_number INTEGER,
  exception TEXT
);

-- Tabela recent_searches
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
);

CREATE INDEX IF NOT EXISTS idx_recent_searches_user ON recent_searches("user", created_at DESC);

-- Tabela whatsapp_config
CREATE TABLE IF NOT EXISTS whatsapp_config (
  id SERIAL PRIMARY KEY,
  access_token TEXT,
  phone_number_id TEXT,
  business_account_id TEXT,
  verify_token TEXT,
  token_expires_at TIMESTAMP
);

-- Tabela damage_reports (PostgreSQL)
CREATE TABLE IF NOT EXISTS damage_reports (
  id SERIAL PRIMARY KEY,
  dr_number TEXT UNIQUE,
  ra_number TEXT,
  contract_number TEXT,
  date DATE,
  client_name TEXT,
  vehicle_plate TEXT,
  vehicle_model TEXT,
  damage_description TEXT,
  damage_location TEXT,
  estimated_cost DECIMAL(10,2),
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  vehicle_damage_image BYTEA
);

-- Inserir utilizadores padrão
INSERT INTO users (username, password_hash, first_name, last_name, is_admin, enabled)
VALUES 
  ('admin', 'scrypt:32768:8:1$yqVZ0M3sPEplemena$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'Admin', 'User', 1, 1),
  ('carlpac82', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'Carlos', 'Pacheco', 1, 1),
  ('dprudente', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'D', 'Prudente', 0, 1),
  ('LP', 'scrypt:32768:8:1$yqVZ0M3sPEemenea$8c5dd3c19ea0a4c8e3f8f0e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8c3e8', 'LP', 'User', 0, 1)
ON CONFLICT (username) DO NOTHING;
