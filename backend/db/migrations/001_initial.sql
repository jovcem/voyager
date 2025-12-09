-- Migration: Initial schema (already applied via schema.sql)
-- This migration exists for tracking purposes only

-- Up
-- Initial schema is already created via docker-entrypoint-initdb.d/schema.sql
-- Tables: stores, products, prices
SELECT 1; -- No-op

-- Down
-- Rolling back the initial schema would drop all tables
-- This should only be done in development
DROP TABLE IF EXISTS prices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
