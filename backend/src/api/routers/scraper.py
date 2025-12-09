"""Scraper endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from ...core.scraper import scrape_url, save_products
from ...core.repository import DatabaseRepository
from ..dependencies import get_repository

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: HttpUrl
    save_to_db: bool = True

@router.post("/scrape")
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    repo: DatabaseRepository = Depends(get_repository)
):
    """Trigger a scrape job"""
    # Scrape immediately
    products = scrape_url(str(request.url))

    if not products:
        raise HTTPException(
            status_code=400,
            detail="No products found or scraping failed"
        )

    # Save to database if requested
    saved_count = 0
    if request.save_to_db:
        saved_count = save_products(products, str(request.url))

    return {
        "status": "completed",
        "url": str(request.url),
        "products_found": len(products),
        "products_saved": saved_count,
        "products": products
    }

@router.get("/stats")
async def get_stats(repo: DatabaseRepository = Depends(get_repository)):
    """Get scraper statistics"""
    stats = repo.get_stats()
    return stats
