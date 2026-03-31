-- Fix timezone for commission_bookings table
-- Convert TIMESTAMP to TIMESTAMP WITH TIME ZONE

-- Alterar coluna created_at para incluir timezone
ALTER TABLE commission_bookings 
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
USING created_at AT TIME ZONE 'UTC';

-- Alterar coluna updated_at para incluir timezone
ALTER TABLE commission_bookings 
ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE 
USING updated_at AT TIME ZONE 'UTC';

-- Definir timezone padrão para Europe/Lisbon nas próximas inserções
ALTER TABLE commission_bookings 
ALTER COLUMN created_at SET DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Lisbon');

ALTER TABLE commission_bookings 
ALTER COLUMN updated_at SET DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Lisbon');

-- Verificar as alterações
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'commission_bookings' 
AND column_name IN ('created_at', 'updated_at');
