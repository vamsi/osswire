from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import create_access_token
from datetime import datetime, timedelta
import httpx
from urllib.parse import urlencode
import json
from oauth_config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI,
    GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_USERINFO_URL,
    GITHUB_AUTH_URL, GITHUB_TOKEN_URL, GITHUB_USERINFO_URL,
    GOOGLE_SCOPES, GITHUB_SCOPES
)

router = APIRouter()

def generate_oauth_state():
    """Generate a random state parameter for OAuth security"""
    import secrets
    return secrets.token_urlsafe(32)

@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    state = generate_oauth_state()
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/auth/google/callback")
async def google_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    if error:
        return RedirectResponse(url="/login?error=oauth_error")
    
    if not code:
        return RedirectResponse(url="/login?error=no_code")
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI
                }
            )
            
            if token_response.status_code != 200:
                return RedirectResponse(url="/login?error=token_error")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return RedirectResponse(url="/login?error=no_token")
            
            # Get user info from Google
            user_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url="/login?error=userinfo_error")
            
            user_data = user_response.json()
            
            # Extract user information
            google_id = user_data.get("id")
            email = user_data.get("email")
            name = user_data.get("name", "")
            picture = user_data.get("picture", "")
            
            if not email:
                return RedirectResponse(url="/login?error=no_email")
            
            # Check if user exists
            user = db.query(User).filter(
                (User.email == email) | 
                (User.oauth_id == str(google_id) & User.oauth_provider == "google")
            ).first()
            
            if not user:
                # Create new user
                username = name.replace(" ", "").lower() if name else email.split("@")[0]
                base_username = username
                counter = 1
                
                # Ensure unique username
                while db.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    oauth_provider="google",
                    oauth_id=str(google_id),
                    avatar_url=picture
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update existing user's OAuth info if needed
                if not user.oauth_provider:
                    user.oauth_provider = "google"
                    user.oauth_id = str(google_id)
                    if picture:
                        user.avatar_url = picture
                    db.commit()
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create access token
            access_token_expires = timedelta(minutes=30)
            jwt_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="access_token", value=jwt_token, httponly=True)
            return response
            
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return RedirectResponse(url="/login?error=oauth_error")

@router.get("/auth/github")
async def github_auth():
    """Initiate GitHub OAuth flow"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    state = generate_oauth_state()
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": " ".join(GITHUB_SCOPES),
        "state": state
    }
    
    auth_url = f"{GITHUB_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/auth/github/callback")
async def github_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    if error:
        return RedirectResponse(url="/login?error=oauth_error")
    
    if not code:
        return RedirectResponse(url="/login?error=no_code")
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                return RedirectResponse(url="/login?error=token_error")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return RedirectResponse(url="/login?error=no_token")
            
            # Get user info from GitHub
            user_response = await client.get(
                GITHUB_USERINFO_URL,
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url="/login?error=userinfo_error")
            
            user_data = user_response.json()
            
            # Extract user information
            github_id = user_data.get("id")
            username = user_data.get("login")
            email = user_data.get("email")
            name = user_data.get("name", "")
            avatar_url = user_data.get("avatar_url", "")
            
            if not username:
                return RedirectResponse(url="/login?error=no_username")
            
            # Check if user exists
            user = db.query(User).filter(
                (User.username == username) | 
                (User.oauth_id == str(github_id) & User.oauth_provider == "github")
            ).first()
            
            if not user:
                # Create new user
                if not email:
                    # Try to get email from GitHub API
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers={
                            "Authorization": f"token {access_token}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                    )
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next((e["email"] for e in emails if e["primary"]), None)
                        if primary_email:
                            email = primary_email
                
                if not email:
                    email = f"{username}@github.com"  # Fallback email
                
                user = User(
                    username=username,
                    email=email,
                    oauth_provider="github",
                    oauth_id=str(github_id),
                    avatar_url=avatar_url
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update existing user's OAuth info if needed
                if not user.oauth_provider:
                    user.oauth_provider = "github"
                    user.oauth_id = str(github_id)
                    if avatar_url:
                        user.avatar_url = avatar_url
                    db.commit()
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create access token
            access_token_expires = timedelta(minutes=30)
            jwt_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="access_token", value=jwt_token, httponly=True)
            return response
            
    except Exception as e:
        print(f"GitHub OAuth error: {e}")
        return RedirectResponse(url="/login?error=oauth_error") 