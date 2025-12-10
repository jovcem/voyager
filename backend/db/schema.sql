-- Voyager Price Scraper Database Schema
-- Consolidated schema with all optimizations

-- Stores table: Information about online stores
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table: Product categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table: Products from stores
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(512) NOT NULL,
    url VARCHAR(1024) NOT NULL,
    image VARCHAR(1024),
    metadata JSONB DEFAULT '{}'::jsonb,
    in_stock BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    last_scraped_at TIMESTAMP,
    name_tsv tsvector,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_products_store_url UNIQUE(store_id, url)
);

-- Prices table: Historical price data
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'MKD',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for stores
CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);

-- Indexes for products
CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_metadata ON products USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_products_in_stock ON products(in_stock);
CREATE INDEX IF NOT EXISTS idx_products_is_deleted ON products(is_deleted) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_products_last_scraped ON products(last_scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_name_tsv ON products USING GIN(name_tsv);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_active_created ON products(is_deleted, created_at DESC) WHERE is_deleted = false;
CREATE INDEX IF NOT EXISTS idx_products_store_created ON products(store_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_category_created ON products(category_id, created_at DESC) WHERE category_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_stock_created ON products(in_stock, created_at DESC) WHERE in_stock = true AND is_deleted = false;

-- Indexes for prices
CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices(product_id);
CREATE INDEX IF NOT EXISTS idx_prices_scraped_at ON prices(scraped_at DESC);

-- Functions and triggers for products

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_products_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS trigger_update_products_updated_at ON products;
CREATE TRIGGER trigger_update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_updated_at();

-- Function to auto-update full-text search vector
CREATE OR REPLACE FUNCTION update_products_name_tsv()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name_tsv = to_tsvector('simple', COALESCE(NEW.name, ''));
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update tsvector
DROP TRIGGER IF EXISTS trigger_update_products_name_tsv ON products;
CREATE TRIGGER trigger_update_products_name_tsv
    BEFORE INSERT OR UPDATE OF name ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_name_tsv();

-- Categories are seeded via migration 002_seed_categories.sql
