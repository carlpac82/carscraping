-- Adicionar campos de configuração de horários à tabela commissioners
-- Execute este script na base de dados do Railway

ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS weekday_start_morning TIME DEFAULT '09:30';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS weekday_end_morning TIME DEFAULT '12:30';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS weekday_start_afternoon TIME DEFAULT '15:00';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS weekday_end_afternoon TIME DEFAULT '17:00';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS sunday_start_morning TIME DEFAULT '09:30';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS sunday_end_morning TIME DEFAULT '12:30';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS sunday_start_afternoon TIME DEFAULT '15:30';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS sunday_end_afternoon TIME DEFAULT '17:00';
ALTER TABLE commissioners ADD COLUMN IF NOT EXISTS time_interval_minutes INTEGER DEFAULT 15;
