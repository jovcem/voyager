-- Migration: Initial consolidated schema
-- This migration represents the initial database schema with all optimizations
-- The actual schema is defined in ../schema.sql and applied via docker-entrypoint-initdb.d

-- Up
-- Schema is already created via docker-entrypoint-initdb.d/schema.sql
SELECT 1; -- No-op

-- Down
-- Rolling back the initial schema would drop all tables
-- This should only be done in development
DROP TRIGGER IF EXISTS trigger_update_products_name_tsv ON products;
DROP TRIGGER IF EXISTS trigger_update_products_updated_at ON products;
DROP FUNCTION IF EXISTS update_products_name_tsv();
DROP FUNCTION IF EXISTS update_products_updated_at();
DROP TABLE IF EXISTS prices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
