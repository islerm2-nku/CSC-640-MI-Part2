"""Authentication and authorization utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user from the token."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, **payload}

# Placeholder for OAuth provider integration
class OAuthProvider:
    """OAuth provider integration (to be implemented)."""
    
    def __init__(self):
        self.client_id = settings.oauth_client_id
        self.client_secret = settings.oauth_client_secret
        self.redirect_uri = settings.oauth_redirect_uri
    
    def get_authorization_url(self) -> str:
        """Get the OAuth authorization URL."""
        # Implement based on your OAuth provider
        raise NotImplementedError("OAuth provider not configured")
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        # Implement based on your OAuth provider
        raise NotImplementedError("OAuth provider not configured")
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from the OAuth provider."""
        # Implement based on your OAuth provider
        raise NotImplementedError("OAuth provider not configured")
