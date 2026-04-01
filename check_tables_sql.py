"""
Admin endpoint to check commissioners tables structure
Run this to verify all required columns exist
"""

CHECK_COMMISSIONERS_TABLES_SQL = """
-- Check and add missing columns to commissioners table
ALTER TABLE commissioners 
    ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
    ADD COLUMN IF NOT EXISTS voucher_prefix VARCHAR(10);

-- Check and add missing columns to commission_bookings table  
ALTER TABLE commission_bookings
    ADD COLUMN IF NOT EXISTS insurance_type VARCHAR(50) DEFAULT 'premium',
    ADD COLUMN IF NOT EXISTS base_price DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS premium_insurance DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS road_tax DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS extras_total DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS rental_days INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS value_adjustment DECIMAL(10, 2) DEFAULT 0;

-- Show table structures
SELECT 'commissioners' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'commissioners'
ORDER BY ordinal_position;

SELECT 'commission_bookings' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'commission_bookings'
ORDER BY ordinal_position;
"""
