-- Migration: Add image column to products table
-- Stores the URL of the product image

-- Up
ALTER TABLE products ADD COLUMN IF NOT EXISTS image VARCHAR(1024);

-- Down
ALTER TABLE products DROP COLUMN IF EXISTS image;
