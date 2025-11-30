"""Authentication endpoints."""
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from datetime import timedelta
from auth_helpers import create_access_token, verify_password, get_current_user
from config import settings

router = APIRouter()

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.get("/oauth/authorize")
async def oauth_authorize():
    """
    Initiate GitHub OAuth flow.
    Redirects user to GitHub authorization page.
    """
    if not settings.oauth_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth not configured. Please set OAUTH_CLIENT_ID in .env"
        )
    
    # Build GitHub authorization URL
    auth_url = (
        f"{settings.oauth_authorization_url}"
        f"?client_id={settings.oauth_client_id}"
        f"&redirect_uri={settings.oauth_redirect_uri}"
        f"&scope=read:user user:email"
    )
    
    return RedirectResponse(url=auth_url)

@router.get("/oauth/callback")
async def oauth_callback(code: str = None, error: str = None):
    """
    GitHub OAuth callback endpoint.
    Exchanges code for access token and retrieves user info.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization code provided"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                settings.oauth_token_url,
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.oauth_client_id,
                    "client_secret": settings.oauth_client_secret,
                    "code": code,
                    "redirect_uri": settings.oauth_redirect_uri,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received"
                )
            
            # Get user info from GitHub
            user_response = await client.get(
                settings.oauth_userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            user_data = user_response.json()
            
            # Create JWT token for our application
            jwt_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
            jwt_token = create_access_token(
                data={
                    "sub": str(user_data.get("id")),
                    "username": user_data.get("login"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email")
                },
                expires_delta=jwt_token_expires
            )
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": user_data.get("id"),
                    "username": user_data.get("login"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "avatar_url": user_data.get("avatar_url")
                }
            }
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTP error occurred: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
