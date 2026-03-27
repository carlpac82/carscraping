-- ============================================================
-- COMMISSION BOOKING SYSTEM - Database Schema
-- ============================================================

-- Table: commissioners
-- Stores commissioner information and credentials
CREATE TABLE IF NOT EXISTS commissioners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    commission_rate DECIMAL(5, 2) DEFAULT 0.00,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: commission_bookings
-- Stores all bookings made by commissioners
CREATE TABLE IF NOT EXISTS commission_bookings (
    id SERIAL PRIMARY KEY,
    commissioner_id INTEGER NOT NULL REFERENCES commissioners(id),
    voucher_number VARCHAR(50) NOT NULL UNIQUE,
    
    -- Client information
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(50) NOT NULL,
    hotel VARCHAR(255),
    room_number VARCHAR(50),
    
    -- Booking details
    pickup_date DATE NOT NULL,
    pickup_time TIME NOT NULL,
    dropoff_date DATE NOT NULL,
    dropoff_time TIME NOT NULL,
    pickup_location TEXT NOT NULL,
    dropoff_location TEXT NOT NULL,
    
    -- Vehicle and extras
    vehicle_group VARCHAR(10) NOT NULL,
    extras JSONB DEFAULT '[]',
    
    -- Additional information
    flight_number VARCHAR(50),
    language VARCHAR(5) NOT NULL DEFAULT 'pt',
    observations TEXT,
    price DECIMAL(10, 2) NOT NULL,
    
    -- Status and tracking
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_commissioner_bookings ON commission_bookings(commissioner_id);
CREATE INDEX IF NOT EXISTS idx_booking_dates ON commission_bookings(pickup_date, dropoff_date);
CREATE INDEX IF NOT EXISTS idx_voucher_number ON commission_bookings(voucher_number);
CREATE INDEX IF NOT EXISTS idx_booking_status ON commission_bookings(status);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_commissioners_updated_at BEFORE UPDATE ON commissioners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_commission_bookings_updated_at BEFORE UPDATE ON commission_bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
