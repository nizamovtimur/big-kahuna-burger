from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Intentionally vulnerable: Direct string interpolation in SQL
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vulnerable function for educational purposes - allows SQL injection
def execute_raw_query(query: str):
    """
    WARNING: This function is intentionally vulnerable to SQL injection
    for educational purposes. Never use this in production!
    """
    # Use a transactional context so DML/DDL statements are committed
    with engine.begin() as connection:
        result = connection.execute(text(query))
        # For SELECT-like statements return rows; for others return empty list
        try:
            if hasattr(result, "returns_rows") and result.returns_rows:
                return result.fetchall()
        except Exception:
            pass
        return []