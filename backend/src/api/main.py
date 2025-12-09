"""FastAPI application initialization"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import products, stores, scraper

app = FastAPI(
    title="Voyager Price Scraper API",
    description="API for tracking product prices from online stores",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(stores.router, prefix="/api/v1/stores", tags=["stores"])
app.include_router(scraper.router, prefix="/api/v1/scraper", tags=["scraper"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Voyager Price Scraper API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    from ..core.repository import DatabaseRepository
    repo = DatabaseRepository()
    success, message = repo.test_connection()

    return {
        "status": "healthy" if success else "unhealthy",
        "database": message
    }
