from fastapi import APIRouter, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user, create_access_token
from datetime import timedelta
import os
import uuid
from PIL import Image
import io

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Ensure upload directory exists
UPLOAD_DIR = "static/uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    # Get current user from token
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    current_user = get_current_user(db, token)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": current_user
    })

@router.post("/settings/username")
async def update_username(
    request: Request,
    new_username: str = Form(...),
    db: Session = Depends(get_db)
):
    # Get current user from token
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    current_user = get_current_user(db, token)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Validate username
    if not new_username or len(new_username.strip()) < 3:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "current_user": current_user,
            "error": "Username must be at least 3 characters long"
        })
    
    new_username = new_username.strip()
    
    # Check if username is already taken
    existing_user = db.query(User).filter(
        User.username == new_username,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "current_user": current_user,
            "error": "Username is already taken"
        })
    
    # Update username
    old_username = current_user.username
    current_user.username = new_username
    db.commit()
    
    # Create new token with updated username
    access_token_expires = timedelta(minutes=30)
    new_token = create_access_token(
        data={"sub": new_username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/settings", status_code=302)
    response.set_cookie(key="access_token", value=new_token, httponly=True)
    return response

@router.post("/settings/avatar")
async def update_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Get current user from token
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    current_user = get_current_user(db, token)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Validate file type
    if not avatar.content_type.startswith("image/"):
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "current_user": current_user,
            "error": "Please upload a valid image file"
        })
    
    try:
        # Read and process image
        image_data = await avatar.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to 200x200 while maintaining aspect ratio
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        # Generate unique filename
        file_extension = avatar.filename.split('.')[-1] if '.' in avatar.filename else 'jpg'
        filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save image
        image.save(file_path, 'JPEG', quality=85)
        
        # Update user's avatar URL
        avatar_url = f"/static/uploads/avatars/{filename}"
        current_user.avatar_url = avatar_url
        db.commit()
        
        return RedirectResponse(url="/settings", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "current_user": current_user,
            "error": f"Error processing image: {str(e)}"
        })

@router.post("/settings/remove-avatar")
async def remove_avatar(
    request: Request,
    db: Session = Depends(get_db)
):
    # Get current user from token
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    current_user = get_current_user(db, token)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Remove avatar URL
    current_user.avatar_url = None
    db.commit()
    
    return RedirectResponse(url="/settings", status_code=302) 