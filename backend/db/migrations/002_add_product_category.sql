-- Migration: Add category column to products table
-- This is an example migration showing how to add a new column

-- Up
ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(100);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Down
DROP INDEX IF EXISTS idx_products_category;
ALTER TABLE products DROP COLUMN IF EXISTS category;
