-- Add missing columns to rental_agreements table
-- Execute this in Railway PostgreSQL Query tab

ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS return_location TEXT;
ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS pickup_location TEXT;
ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS pickup_date TEXT;
ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS return_date TEXT;
ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS client_name TEXT;
ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS client_email TEXT;

-- Verify columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'rental_agreements'
ORDER BY ordinal_position;
