-- Rental SaaS Database Initialization Script
-- This script sets up the initial database structure and data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'employee', 'customer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE reservation_status AS ENUM ('pending', 'confirmed', 'active', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (will be created by SQLAlchemy migrations)
-- These are just examples of what should be indexed

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Insert default data after tables are created
-- This will be handled by the Flask application initialization

-- Create a function to generate reservation codes
CREATE OR REPLACE FUNCTION generate_reservation_code()
RETURNS TEXT AS $$
DECLARE
    code TEXT;
    exists_check INTEGER;
BEGIN
    LOOP
        -- Generate a random 8-character code
        code := 'RES' || LPAD(FLOOR(RANDOM() * 100000)::TEXT, 5, '0');
        
        -- Check if it exists (this will work after the reservations table is created)
        -- For now, just return the code
        RETURN code;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create a function to generate customer codes
CREATE OR REPLACE FUNCTION generate_customer_code()
RETURNS TEXT AS $$
DECLARE
    code TEXT;
BEGIN
    -- Generate a customer code based on timestamp and random number
    code := 'CLI' || EXTRACT(YEAR FROM NOW())::TEXT || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Create a function to calculate rental duration in hours
CREATE OR REPLACE FUNCTION calculate_rental_hours(start_date TIMESTAMP, end_date TIMESTAMP)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(EPOCH FROM (end_date - start_date)) / 3600;
END;
$$ LANGUAGE plpgsql;

-- Create a function to calculate rental price based on duration
CREATE OR REPLACE FUNCTION calculate_rental_price(
    hourly_price DECIMAL,
    daily_price DECIMAL,
    weekly_price DECIMAL,
    monthly_price DECIMAL,
    hours INTEGER
)
RETURNS DECIMAL AS $$
DECLARE
    days INTEGER;
    weeks INTEGER;
    months INTEGER;
    total_price DECIMAL := 0;
BEGIN
    -- Calculate months, weeks, days, and remaining hours
    months := hours / (24 * 30);
    hours := hours % (24 * 30);
    
    weeks := hours / (24 * 7);
    hours := hours % (24 * 7);
    
    days := hours / 24;
    hours := hours % 24;
    
    -- Calculate price based on best rates
    IF monthly_price IS NOT NULL AND months > 0 THEN
        total_price := total_price + (months * monthly_price);
    END IF;
    
    IF weekly_price IS NOT NULL AND weeks > 0 THEN
        total_price := total_price + (weeks * weekly_price);
    ELSIF daily_price IS NOT NULL AND weeks > 0 THEN
        total_price := total_price + (weeks * 7 * daily_price);
    END IF;
    
    IF daily_price IS NOT NULL AND days > 0 THEN
        total_price := total_price + (days * daily_price);
    ELSIF hourly_price IS NOT NULL AND days > 0 THEN
        total_price := total_price + (days * 24 * hourly_price);
    END IF;
    
    IF hourly_price IS NOT NULL AND hours > 0 THEN
        total_price := total_price + (hours * hourly_price);
    END IF;
    
    RETURN total_price;
END;
$$ LANGUAGE plpgsql;

-- Log successful initialization
INSERT INTO pg_stat_statements_info (dealloc) VALUES (0) ON CONFLICT DO NOTHING;

-- Create a simple log table for tracking initialization
CREATE TABLE IF NOT EXISTS initialization_log (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO initialization_log (message) VALUES ('Database initialization script completed successfully');

