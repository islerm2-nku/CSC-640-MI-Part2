"""Database migration script - creates all tables for the telemetry API using SQLAlchemy ORM."""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add app directory to path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Base

def get_database_url():
    """Get database URL from environment variables."""
    host = os.getenv('DB_HOST', 'db')
    port = os.getenv('DB_PORT', '3306')
    database = os.getenv('DB_DATABASE', 'app')
    user = os.getenv('DB_USER', 'appuser')
    password = os.getenv('DB_PASSWORD', 'apppass')
    
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

def create_tables():
    """Create all database tables using SQLAlchemy ORM."""
    try:
        # Create engine
        database_url = get_database_url()
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        print("Connected to MySQL database")
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        # Print created tables
        tables = ['session_info', 'weather', 'driver', 'attribute_values']
        for table in tables:
            print(f"✓ Created {table} table")
        
        print(f"\n✅ Migration complete: All tables created successfully")
        
    except SQLAlchemyError as e:
        print(f"❌ Error connecting to MySQL: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'engine' in locals():
            engine.dispose()
            print("Database connection closed")

if __name__ == "__main__":
    create_tables()