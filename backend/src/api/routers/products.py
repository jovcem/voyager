"""Product endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from ...core.repository import DatabaseRepository
from ..dependencies import get_repository

router = APIRouter()

@router.get("/")
async def list_products(
    limit: int = 20,
    repo: DatabaseRepository = Depends(get_repository)
):
    """List recent products with prices"""
    products = repo.list_recent_products(limit=limit)
    return {"products": products, "count": len(products)}

@router.get("/search")
async def search_products(
    q: str,
    limit: int = 50,
    repo: DatabaseRepository = Depends(get_repository)
):
    """Search products by name"""
    products = repo.search_products(q, limit=limit)
    return {"products": products, "count": len(products), "query": q}

@router.get("/{product_id}")
async def get_product(
    product_id: int,
    repo: DatabaseRepository = Depends(get_repository)
):
    """Get product by ID"""
    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{product_id}/history")
async def get_price_history(
    product_id: int,
    limit: int = 100,
    repo: DatabaseRepository = Depends(get_repository)
):
    """Get price history for a product"""
    history = repo.get_price_history(product_id, limit=limit)
    return {"product_id": product_id, "history": history, "count": len(history)}
