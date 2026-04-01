-- Migration: Add login_attempts table for rate limiting
-- Created: 2026-03-06
-- Description: Creates the login_attempts table to track login attempts
--              for brute force protection and rate limiting.

-- Create login_attempts table
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address VARCHAR(45) DEFAULT 'unknown',
    attempt_time TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_username_time ON login_attempts (username, attempt_time);
CREATE INDEX IF NOT EXISTS idx_attempt_time ON login_attempts (attempt_time);

-- Add comment to table
COMMENT ON TABLE login_attempts IS 'Tracks login attempts for rate limiting and security monitoring';
COMMENT ON COLUMN login_attempts.username IS 'Username that attempted to log in';
COMMENT ON COLUMN login_attempts.success IS 'Whether the login attempt was successful';
COMMENT ON COLUMN login_attempts.ip_address IS 'IP address of the login attempt (for audit purposes)';
COMMENT ON COLUMN login_attempts.attempt_time IS 'Timestamp of the login attempt';
