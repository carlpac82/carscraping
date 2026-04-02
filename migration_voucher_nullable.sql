-- Migration: Allow NULL values in voucher_number column
-- This allows manual bookings to have no voucher number unless explicitly provided

-- Step 1: Drop the existing UNIQUE constraint
ALTER TABLE commission_bookings DROP CONSTRAINT IF EXISTS commission_bookings_voucher_number_key;

-- Step 2: Allow NULL values in the column
ALTER TABLE commission_bookings ALTER COLUMN voucher_number DROP NOT NULL;

-- Step 3: Create a partial UNIQUE index that only applies to non-NULL values
-- This allows multiple NULL values but ensures non-NULL values are unique
CREATE UNIQUE INDEX commission_bookings_voucher_number_unique 
ON commission_bookings (voucher_number) 
WHERE voucher_number IS NOT NULL;
