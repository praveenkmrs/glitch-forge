"""Database session management.

This module provides:
1. Database engine creation
2. Session factory
3. Dependency injection for FastAPI

Key Concepts:
- Engine: The connection pool to the database
- SessionLocal: Factory for creating database sessions
- Session: Individual database connection (opened per request, closed after)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create database engine
# echo=True in development shows SQL queries (great for learning!)
engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using (handles disconnects)
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Allow 10 extra connections if pool is full
)

# Session factory
# Creates new Session objects
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit (we control transactions)
    autoflush=False,  # Don't auto-flush (we control when to write)
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions.

    Usage in route handlers:
        @app.get("/items")
        async def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items

    How it works:
    1. Creates a new session for each request
    2. Yields the session to the route handler
    3. Closes the session after the request (even if there's an error)

    This ensures:
    - No connection leaks
    - Proper transaction handling
    - Thread safety (each request gets its own session)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
