-- Add signature and receiver name columns to commission_bookings table
ALTER TABLE commission_bookings 
ADD COLUMN IF NOT EXISTS commission_signature TEXT,
ADD COLUMN IF NOT EXISTS commission_receiver_name VARCHAR(255);
