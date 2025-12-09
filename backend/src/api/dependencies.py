"""Dependency injection for FastAPI"""
from ..core.repository import DatabaseRepository

def get_repository() -> DatabaseRepository:
    """Get database repository instance"""
    return DatabaseRepository()
