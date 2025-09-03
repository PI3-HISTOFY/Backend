# app/database/__init__.py
from .database import Base, engine, get_db
from .databaseNSQL import historias_collection

__all__ = ["Base", "engine", "get_db", "historias_collection"]
