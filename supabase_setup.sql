# SmartFleet 2.0 — Supabase PostgreSQL & PostGIS Database Setup

This script sets up the complete production database schema on **Supabase** for SmartFleet 2.0.

> [!NOTE]
> **How to execute:**
> 1. Open your Supabase Dashboard: [https://supabase.com/dashboard/project/pnfleqdwvbnerpjwqoqe](https://supabase.com/dashboard/project/pnfleqdwvbnerpjwqoqe)
> 2. Navigate to **SQL Editor** in the left sidebar.
> 3. Click **New Query**, paste the SQL script below, and click **Run**.

---

### Production SQL Migration Script

```sql
-- =============================================================================
-- SMARTFLEET 2.0 - PRODUCTION DATABASE SCHEMA FOR SUPABASE (POSTGRESQL + POSTGIS)
-- Multi-tenant Fleet Tracking, POD, Realtime Telemetry, Geofencing
-- Compatible with: Supabase PostgreSQL 15+, Supabase Auth / Custom JWT, RLS
-- =============================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 2. ENUM TYPES
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'driver', 'dispatcher');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'truck_status') THEN
        CREATE TYPE truck_status AS ENUM ('available', 'on_trip', 'in_workshop', 'offline');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trip_status') THEN
        CREATE TYPE trip_status AS ENUM ('waiting', 'accepted', 'running', 'delivered', 'cancelled');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alert_severity') THEN
        CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical');
    END IF;
END $$;

-- 3. USERS TABLE
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'driver',
    hashed_password VARCHAR(255),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. DRIVERS TABLE
CREATE TABLE IF NOT EXISTS public.drivers (
    id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    experience_years INT NOT NULL DEFAULT 0,
    current_truck_plate VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    total_trips_completed INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. TRUCKS TABLE
CREATE TABLE IF NOT EXISTS public.trucks (
    plate VARCHAR(20) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    capacity_tons NUMERIC(5,2) NOT NULL DEFAULT 25.0,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    assigned_driver_id UUID REFERENCES public.drivers(id) ON DELETE SET NULL,
    last_latitude DOUBLE PRECISION,
    last_longitude DOUBLE PRECISION,
    last_heading DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    last_speed_kmh DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    last_telemetry_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. TRIPS TABLE
CREATE TABLE IF NOT EXISTS public.trips (
    id VARCHAR(20) PRIMARY KEY,
    origin_city VARCHAR(100) NOT NULL,
    origin_code VARCHAR(10) NOT NULL,
    origin_lat DOUBLE PRECISION NOT NULL,
    origin_lng DOUBLE PRECISION NOT NULL,
    dest_city VARCHAR(100) NOT NULL,
    dest_code VARCHAR(10) NOT NULL,
    dest_lat DOUBLE PRECISION NOT NULL,
    dest_lng DOUBLE PRECISION NOT NULL,
    cargo_title VARCHAR(150) NOT NULL,
    weight_tons NUMERIC(5,2) NOT NULL,
    truck_plate VARCHAR(20) NOT NULL REFERENCES public.trucks(plate) ON DELETE RESTRICT,
    driver_id UUID NOT NULL REFERENCES public.drivers(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',
    scheduled_start TIMESTAMPTZ NOT NULL DEFAULT now(),
    actual_started_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    total_distance_km NUMERIC(7,2) NOT NULL,
    distance_done_km NUMERIC(7,2) NOT NULL DEFAULT 0.0,
    allowance_amount INT NOT NULL DEFAULT 1500,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. PROOF OF DELIVERY (POD)
CREATE TABLE IF NOT EXISTS public.proof_of_delivery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id VARCHAR(20) UNIQUE NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
    otp_code VARCHAR(10) NOT NULL,
    otp_verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    photo_url TEXT NOT NULL,
    signature_svg TEXT NOT NULL,
    recipient_name VARCHAR(100),
    recipient_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. TELEMETRY LOGS (Time-series GPS data)
CREATE TABLE IF NOT EXISTS public.telemetry_logs (
    id BIGSERIAL PRIMARY KEY,
    truck_plate VARCHAR(20) NOT NULL REFERENCES public.trucks(plate) ON DELETE CASCADE,
    trip_id VARCHAR(20) REFERENCES public.trips(id) ON DELETE SET NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    heading DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    speed_kmh DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    battery_level INT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. OPERATIONAL ALERTS
CREATE TABLE IF NOT EXISTS public.operational_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    truck_plate VARCHAR(20) NOT NULL REFERENCES public.trucks(plate) ON DELETE CASCADE,
    trip_id VARCHAR(20) REFERENCES public.trips(id) ON DELETE SET NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_users_phone ON public.users(phone);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_drivers_license ON public.drivers(license_number);
CREATE INDEX IF NOT EXISTS idx_trucks_status ON public.trucks(status);
CREATE INDEX IF NOT EXISTS idx_trips_status ON public.trips(status);
CREATE INDEX IF NOT EXISTS idx_trips_driver ON public.trips(driver_id);
CREATE INDEX IF NOT EXISTS idx_trips_truck ON public.trips(truck_plate);
CREATE INDEX IF NOT EXISTS idx_telemetry_truck_time ON public.telemetry_logs(truck_plate, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON public.operational_alerts(is_resolved, created_at DESC);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) & POLICIES
-- =============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trucks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.proof_of_delivery ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.telemetry_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.operational_alerts ENABLE ROW LEVEL SECURITY;

-- Allow Service Role and authenticated backend full access
DROP POLICY IF EXISTS "Service role full access on users" ON public.users;
CREATE POLICY "Service role full access on users" ON public.users FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on drivers" ON public.drivers;
CREATE POLICY "Service role full access on drivers" ON public.drivers FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on trucks" ON public.trucks;
CREATE POLICY "Service role full access on trucks" ON public.trucks FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on trips" ON public.trips;
CREATE POLICY "Service role full access on trips" ON public.trips FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on pod" ON public.proof_of_delivery;
CREATE POLICY "Service role full access on pod" ON public.proof_of_delivery FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on telemetry" ON public.telemetry_logs;
CREATE POLICY "Service role full access on telemetry" ON public.telemetry_logs FOR ALL USING (true);

DROP POLICY IF EXISTS "Service role full access on alerts" ON public.operational_alerts;
CREATE POLICY "Service role full access on alerts" ON public.operational_alerts FOR ALL USING (true);

-- =============================================================================
-- SUPABASE REALTIME REPLICATION
-- Enable real-time WebSocket events for fleet monitoring
-- =============================================================================
DO $$ BEGIN
    BEGIN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.trips, public.trucks, public.operational_alerts, public.telemetry_logs;
    EXCEPTION WHEN duplicate_object THEN
        NULL;
    END;
END $$;

-- =============================================================================
-- SEED DATA (KERALA FLEET ECOSYSTEM)
-- =============================================================================
-- 1. Admin & Drivers
INSERT INTO public.users (id, phone, full_name, role, hashed_password) VALUES
('2a500149-3124-4529-9221-32ddf5dfd299', '+91 98950 00000', 'Fleet Manager (Kochi HQ)', 'admin', '$2b$12$e0X76r5P3M1v87s3Mv3aEOyXw3zP2K8Qx3x3x3x3x3x3x3x3x3x3x'),
('3b600250-4235-5630-a332-43eef6efd3aa', '+91 94471 23456', 'Muhammed Shafi', 'driver', '$2b$12$e0X76r5P3M1v87s3Mv3aEOyXw3zP2K8Qx3x3x3x3x3x3x3x3x3x3x'),
('4c700361-5346-6741-b443-54ffa7fea4bb', '+91 98462 34567', 'Suresh Kumar', 'driver', '$2b$12$e0X76r5P3M1v87s3Mv3aEOyXw3zP2K8Qx3x3x3x3x3x3x3x3x3x3x'),
('5d800472-6457-7852-c554-6500b80fb5cc', '+91 97453 45678', 'Rajesh Pillai', 'driver', '$2b$12$e0X76r5P3M1v87s3Mv3aEOyXw3zP2K8Qx3x3x3x3x3x3x3x3x3x3x')
ON CONFLICT (phone) DO NOTHING;

INSERT INTO public.drivers (id, license_number, experience_years, current_truck_plate, status, total_trips_completed) VALUES
('3b600250-4235-5630-a332-43eef6efd3aa', 'KL-07-2015-0082910', 8, 'KL 07 CD 4589', 'available', 142),
('4c700361-5346-6741-b443-54ffa7fea4bb', 'KL-11-2017-0043129', 6, 'KL 11 BH 8920', 'available', 98),
('5d800472-6457-7852-c554-6500b80fb5cc', 'KL-01-2012-0091823', 12, 'KL 01 CA 1290', 'available', 215)
ON CONFLICT (id) DO NOTHING;

-- 2. Trucks
INSERT INTO public.trucks (plate, model, capacity_tons, status, assigned_driver_id, last_latitude, last_longitude, last_heading, last_speed_kmh, last_telemetry_at) VALUES
('KL 07 CD 4589', 'BharatBenz 2823R (28T Heavy Multi-Axle)', 28.0, 'on_trip', '3b600250-4235-5630-a332-43eef6efd3aa', 10.5276, 76.2144, 45.0, 58.5, now()),
('KL 11 BH 8920', 'Tata Prima 3530.K (35T Multi-Axle Tipper)', 35.0, 'on_trip', '4c700361-5346-6741-b443-54ffa7fea4bb', 11.2588, 75.7804, 180.0, 42.0, now()),
('KL 01 CA 1290', 'Ashok Leyland 4220 (42T Haulage)', 42.0, 'available', '5d800472-6457-7852-c554-6500b80fb5cc', 8.5241, 76.9366, 0.0, 0.0, now()),
('KL 08 AP 3412', 'Eicher Pro 6028 (28T Cargo Carrier)', 28.0, 'in_workshop', NULL, 10.0159, 76.3419, 0.0, 0.0, now())
ON CONFLICT (plate) DO UPDATE SET status = EXCLUDED.status;

-- 3. Trips
INSERT INTO public.trips (id, origin_city, origin_code, origin_lat, origin_lng, dest_city, dest_code, dest_lat, dest_lng, cargo_title, weight_tons, truck_plate, driver_id, status, scheduled_start, actual_started_at, total_distance_km, distance_done_km, allowance_amount, is_paid) VALUES
('TRIP-9821', 'Kochi Port (Willingdon)', 'COK', 9.9312, 76.2673, 'Kozhikode Bypass Yard', 'CCJ', 11.2588, 75.7804, 'Container Freight (Electronics & Spices)', 22.4, 'KL 07 CD 4589', '3b600250-4235-5630-a332-43eef6efd3aa', 'running', now() - INTERVAL '3 hours', now() - INTERVAL '3 hours', 182.0, 95.0, 1800, false),
('TRIP-9822', 'Kozhikode Industrial Area', 'CCJ', 11.2588, 75.7804, 'Kannur New Cargo Terminal', 'CNN', 11.8745, 75.3704, 'Cement Sacks & Steel TMT Bars', 31.0, 'KL 11 BH 8920', '4c700361-5346-6741-b443-54ffa7fea4bb', 'running', now() - INTERVAL '1 hour', now() - INTERVAL '1 hour', 92.0, 28.0, 1200, false),
('TRIP-9820', 'Trivandrum Petro Hub', 'TRV', 8.5241, 76.9366, 'Kochi Refinery Gate 4', 'COK', 9.9312, 76.2673, 'Bulk Polymer Granules', 38.5, 'KL 01 CA 1290', '5d800472-6457-7852-c554-6500b80fb5cc', 'delivered', now() - INTERVAL '1 day', now() - INTERVAL '1 day', 205.0, 205.0, 2200, true)
ON CONFLICT (id) DO NOTHING;

-- 4. Sample Alerts
INSERT INTO public.operational_alerts (id, truck_plate, trip_id, severity, title, description, is_resolved) VALUES
('a1111111-1111-1111-1111-111111111111', 'KL 07 CD 4589', 'TRIP-9821', 'warning', 'NH 66 Edappally Bypass Congestion', 'Heavy transit delay detected near Vyttila mobility corridor (+25 mins ETA impact)', false),
('a2222222-2222-2222-2222-222222222222', 'KL 08 AP 3412', NULL, 'critical', 'Scheduled Brake Liners Replacement', 'Brake pad sensor flagged maintenance threshold reached at Kalamassery workshop', false)
ON CONFLICT (id) DO NOTHING;
```
