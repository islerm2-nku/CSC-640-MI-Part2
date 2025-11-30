"""Main FastAPI application."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine
from models import Base

# Create FastAPI app
app = FastAPI(
    title="iRacing Telemetry API",
    description="""
    FastAPI-based telemetry API with GitHub OAuth authentication.
    
    ## Authentication
    
    This API uses GitHub OAuth for authentication. To get an access token:
    
    1. Visit the OAuth authorization page: http://localhost/auth/oauth/authorize
    2. Authorize with GitHub
    3. Copy the `access_token` from the response
    4. Click the **Authorize** button (🔒) at the top of this page
    5. Paste your token in the "Value" field
    6. Click "Authorize" to use protected endpoints
    
    ## Protected Endpoints
    
    Endpoints marked with a lock icon (🔒) require authentication.
    """,    
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (if not using migrations)
# Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "iRacing Telemetry API - Phase 2",
        "version": "2.0.0",
        "docs": "/docs",
        "oauth_login": "/auth/oauth/authorize"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Include routers
from routers import sessions, telemetry, auth
app.include_router(auth.router, prefix="/auth", tags=["authentication"], include_in_schema=False)
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
