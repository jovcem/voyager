"""Store endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from ...core.repository import DatabaseRepository
from ..dependencies import get_repository

router = APIRouter()

@router.get("/")
async def list_stores(repo: DatabaseRepository = Depends(get_repository)):
    """List all stores"""
    stores = repo.list_stores()
    return {"stores": stores, "count": len(stores)}

@router.get("/{store_id}")
async def get_store(
    store_id: int,
    repo: DatabaseRepository = Depends(get_repository)
):
    """Get store by ID"""
    store = repo.get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@router.get("/stats")
async def get_stats(repo: DatabaseRepository = Depends(get_repository)):
    """Get database statistics"""
    stats = repo.get_stats()
    return stats
