"""Application configuration using pydantic-settings."""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    db_driver: str = "mysql"
    db_host: str = "db"
    db_port: int = 3306
    db_database: str = "app"
    db_user: str = "appuser"
    db_password: str = "apppass"
    
    # GitHub OAuth
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_redirect_uri: str = "http://localhost/auth/callback"
    oauth_authorization_url: str = "https://github.com/login/oauth/authorize"
    oauth_token_url: str = "https://github.com/login/oauth/access_token"
    oauth_userinfo_url: str = "https://api.github.com/user"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
