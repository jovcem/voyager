# Voyager Backend - New Structure

The codebase has been reorganized into a professional Python project structure with separate API and CLI interfaces.

## New Directory Structure

```
backend/
├── src/                          # Main source code
│   ├── api/                      # FastAPI application
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── dependencies.py      # Dependency injection
│   │   └── routers/             # API endpoints
│   │       ├── products.py      # Product endpoints
│   │       ├── stores.py        # Store endpoints
│   │       └── scraper.py       # Scraper trigger endpoints
│   │
│   ├── cli/                      # CLI application
│   │   └── commands.py          # Click commands
│   │
│   ├── core/                     # Shared business logic
│   │   ├── config.py            # Configuration
│   │   ├── repository.py        # Database access layer
│   │   └── scraper.py           # Scraping logic
│   │
│   └── scrapers/                 # Site-specific scrapers
│       ├── base.py              # Base scraper class
│       └── neptun.py            # Neptun scraper
│
├── db/                           # Database
│   ├── schema.sql               # Initial schema
│   └── migrations/              # Database migrations
│
├── scripts/                      # Entry points
│   ├── cli.py                   # CLI entry point
│   └── migrate.py               # Migration tool
│
├── docs/                         # Documentation
├── examples/                     # Example code
└── tests/                        # Tests (future)
```

## How to Use

### 1. Install Dependencies

```bash
cd /Users/jovchemalakovski/code/voyager/backend
pip install -r requirements.txt
```

### 2. Run the CLI

```bash
# Show version
python scripts/cli.py --version

# Test database connection
python scripts/cli.py test

# Scrape a URL
python scripts/cli.py scrape https://example.com --save-db

# List products
python scripts/cli.py list

# Run migrations
python scripts/cli.py migrate status
python scripts/cli.py migrate up
```

### 3. Run the API

```bash
# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Access the API
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - OpenAPI schema: http://localhost:8000/openapi.json
```

### 4. API Endpoints

#### Products
- `GET /api/v1/products` - List recent products (default: 20)
- `GET /api/v1/products/search?q={query}` - Search products by name
- `GET /api/v1/products/{product_id}` - Get single product
- `GET /api/v1/products/{product_id}/history` - Get price history

#### Stores
- `GET /api/v1/stores` - List all stores
- `GET /api/v1/stores/{store_id}` - Get single store
- `GET /api/v1/stores/stats` - Get database statistics

#### Scraper
- `POST /api/v1/scraper/scrape` - Trigger scrape job
  ```json
  {
    "url": "https://example.com",
    "save_to_db": true
  }
  ```
- `GET /api/v1/scraper/stats` - Get scraper statistics

## What Changed

### Files Moved
- `cli.py` → `src/cli/commands.py`
- `repository.py` → `src/core/repository.py`
- `scraper.py` → `src/core/scraper.py`
- `BaseScraper.py` → `src/scrapers/base.py`
- `NeptunScraper.py` → `src/scrapers/neptun.py`
- `schema.sql` → `db/schema.sql`
- `migrations/` → `db/migrations/`
- `migrate.py` → `scripts/migrate.py`
- Documentation → `docs/`

### Files Created
- `src/api/main.py` - FastAPI application
- `src/api/routers/*.py` - API endpoint routers
- `src/core/config.py` - Centralized configuration
- `scripts/cli.py` - CLI entry point wrapper

### Files Updated
- `docker-compose.yml` - Updated schema.sql path
- `requirements.txt` - Added FastAPI, uvicorn, pydantic
- All imports updated to use new structure

## Benefits

1. **Clean Separation**: API and CLI are separate but share core logic
2. **Professional Structure**: Follows Python best practices
3. **Easy to Test**: Clear module boundaries
4. **Scalable**: Easy to add new endpoints or commands
5. **Auto-documented API**: FastAPI generates interactive docs

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Test CLI: `python scripts/cli.py test`
3. Start API: `uvicorn src.api.main:app --reload`
4. Visit http://localhost:8000/docs to explore the API

## Notes

- Both CLI and API share the same `repository.py` and database
- No code duplication - core logic is in `src/core/`
- Can run CLI and API simultaneously
- All original functionality preserved
