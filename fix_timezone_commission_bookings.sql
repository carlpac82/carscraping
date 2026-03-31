-- Fix timezone for all tables
-- Convert TIMESTAMP to TIMESTAMP WITH TIME ZONE
-- Timezone: Europe/Lisbon (UTC+0 no inverno, UTC+1 no verão)

-- ============================================
-- 1. COMMISSION_BOOKINGS (Reservas dos Comissionistas)
-- ============================================
ALTER TABLE commission_bookings 
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
USING created_at AT TIME ZONE 'UTC';

ALTER TABLE commission_bookings 
ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE 
USING updated_at AT TIME ZONE 'UTC';

ALTER TABLE commission_bookings 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE commission_bookings 
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 2. COMMISSIONERS (Comissionistas)
-- ============================================
ALTER TABLE commissioners 
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
USING created_at AT TIME ZONE 'UTC';

ALTER TABLE commissioners 
ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE 
USING updated_at AT TIME ZONE 'UTC';

ALTER TABLE commissioners 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE commissioners 
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 3. VEHICLE_INSPECTIONS (Inspeções)
-- ============================================
-- Nota: vehicle_inspections só tem created_at, não tem updated_at
ALTER TABLE vehicle_inspections 
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
USING created_at AT TIME ZONE 'UTC';

ALTER TABLE vehicle_inspections 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 4. BOOKINGS (Reservas antigas - se existir)
-- ============================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'bookings') THEN
        ALTER TABLE bookings 
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
        USING created_at AT TIME ZONE 'UTC';
        
        ALTER TABLE bookings 
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE 
        USING updated_at AT TIME ZONE 'UTC';
        
        ALTER TABLE bookings 
        ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;
        
        ALTER TABLE bookings 
        ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- ============================================
-- 5. Configurar timezone da sessão PostgreSQL
-- ============================================
-- Isto garante que todas as operações usam o timezone de Lisboa
ALTER DATABASE railway SET timezone TO 'Europe/Lisbon';

-- Verificar as alterações
SELECT 
    table_name, 
    column_name, 
    data_type, 
    column_default 
FROM information_schema.columns 
WHERE table_name IN ('commission_bookings', 'commissioners', 'vehicle_inspections', 'bookings')
AND column_name IN ('created_at', 'updated_at')
ORDER BY table_name, column_name;
