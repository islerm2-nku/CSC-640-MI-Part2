"""Database connection and configuration."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Construct database URL from environment variables."""
    db_user = os.getenv('DB_USER', 'appuser')
    db_password = os.getenv('DB_PASSWORD', 'apppass')
    db_host = os.getenv('DB_HOST', 'db')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_DATABASE', 'app')
    
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create SQLAlchemy engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency function to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
