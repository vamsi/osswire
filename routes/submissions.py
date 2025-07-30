from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Post, User, Vote, LicenseType, Comment, CategoryType, LanguageType, SubmissionType, Favorite
from auth import get_current_user, verify_token
from datetime import datetime, timedelta
from typing import Optional
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from utils import get_thumbnail_data
from url_validator import validate_oss_url
import math

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time like '2 hours ago'"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            if weeks == 1:
                return "1 week ago"
            else:
                return f"{weeks} weeks ago"
        else:
            months = diff.days // 30
            if months == 1:
                return "1 month ago"
            else:
                return f"{months} months ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        if hours == 1:
            return "1 hour ago"
        else:
            return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        if minutes == 1:
            return "1 minute ago"
        else:
            return f"{minutes} minutes ago"
    else:
        return "just now"

def get_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    return get_current_user(db, token)

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    license_filter: Optional[str] = Query(None),
    date_filter: Optional[str] = Query(None),
    min_score: Optional[str] = Query(None),
    sort_by: str = Query("ranked"),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Post).join(User)
    
    # Apply filters
    if license_filter:
        query = query.filter(Post.license == LicenseType(license_filter))
    
    if date_filter:
        if date_filter == "day":
            cutoff = datetime.utcnow() - timedelta(days=1)
        elif date_filter == "week":
            cutoff = datetime.utcnow() - timedelta(weeks=1)
        elif date_filter == "month":
            cutoff = datetime.utcnow() - timedelta(days=30)
        else:
            cutoff = None
        
        if cutoff:
            query = query.filter(Post.created_at >= cutoff)
    
    if min_score and min_score.strip():
        try:
            min_score_int = int(min_score)
            query = query.filter(Post.points >= min_score_int)
        except ValueError:
            # Invalid number, ignore the filter
            pass
    
    # Get total count for pagination
    total_posts = query.count()
    posts_per_page = 20
    total_pages = math.ceil(total_posts / posts_per_page)
    
    # Ensure page is within bounds
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Apply sorting and pagination
    if sort_by == "ranked":
        posts = query.order_by(desc(Post.points)).offset((page - 1) * posts_per_page).limit(posts_per_page).all()
    else:  # latest
        posts = query.order_by(desc(Post.created_at)).offset((page - 1) * posts_per_page).limit(posts_per_page).all()
    
    # Get current user
    current_user = get_user_from_cookie(request, db)
    
    # Get user's favorites if logged in
    user_favorites = set()
    if current_user:
        favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
        user_favorites = {fav.post_id for fav in favorites}
    
    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "posts": posts,
            "current_user": current_user,
            "user_favorites": user_favorites,
            "license_types": LicenseType,
            "current_filters": {
                "license": license_filter,
                "date": date_filter,
                "min_score": min_score if min_score and min_score.strip() else None,
                "sort_by": sort_by
            },
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_posts": total_posts,
                "posts_per_page": posts_per_page
            },
            "get_thumbnail_data": get_thumbnail_data,
            "format_relative_time": format_relative_time
        }
    )

@router.get("/submit", response_class=HTMLResponse)
async def submit_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "submit.html", 
        {
            "request": request, 
            "license_types": LicenseType,
            "category_types": CategoryType,
            "language_types": LanguageType,
            "submission_types": SubmissionType
        }
    )

@router.post("/submit")
async def submit_post(
    request: Request,
    title: str = Form(...),
    url: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    license: str = Form(...),
    category: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    submission_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not title:
        return templates.TemplateResponse(
            "submit.html", 
            {"request": request, "error": "Title is required", "license_types": LicenseType}
        )
    
    if not url and not content:
        return templates.TemplateResponse(
            "submit.html", 
            {"request": request, "error": "Either URL or content is required", "license_types": LicenseType}
        )
    
    try:
        license_enum = LicenseType(license)
    except ValueError:
        return templates.TemplateResponse(
            "submit.html", 
            {"request": request, "error": "Invalid license", "license_types": LicenseType}
        )
    
    # Validate URL if provided
    if url:
        validation_result = validate_oss_url(url)
        if not validation_result.valid:
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "error": f"URL validation failed: {validation_result.reason}",
                    "title": title,
                    "url": url,
                    "content": content,
                    "license": license
                }
            )
        # Use the normalized URL
        url = validation_result.normalized_url
    
    # Parse tag enums
    category_enum = None
    language_enum = None
    submission_type_enum = None
    
    if category:
        try:
            category_enum = CategoryType(category)
        except ValueError:
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "error": "Invalid category",
                    "title": title,
                    "url": url,
                    "content": content,
                    "license": license,
                    "category": category,
                    "language": language,
                    "submission_type": submission_type
                }
            )
    
    if language:
        try:
            language_enum = LanguageType(language)
        except ValueError:
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "error": "Invalid language",
                    "title": title,
                    "url": url,
                    "content": content,
                    "license": license,
                    "category": category,
                    "language": language,
                    "submission_type": submission_type
                }
            )
    
    if submission_type:
        try:
            submission_type_enum = SubmissionType(submission_type)
        except ValueError:
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "error": "Invalid submission type",
                    "title": title,
                    "url": url,
                    "content": content,
                    "license": license,
                    "category": category,
                    "language": language,
                    "submission_type": submission_type
                }
            )
    
    new_post = Post(
        title=title,
        url=url,
        content=content,
        license=license_enum,
        category=category_enum,
        language=language_enum,
        submission_type=submission_type_enum,
        created_by=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return RedirectResponse(url=f"/post/{new_post.id}", status_code=302)

@router.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(
    request: Request,
    post_id: str,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Build comment tree
    from routes.comments import build_comment_tree
    comments = db.query(Comment).filter(Comment.submission_id == post_id).all()
    post.comments = build_comment_tree(comments)
    
    current_user = get_user_from_cookie(request, db)
    
    return templates.TemplateResponse(
        "post.html", 
        {"request": request, "post": post, "current_user": current_user}
    )

@router.post("/vote/{post_id}")
async def vote_post(
    request: Request,
    post_id: str,
    vote_type: int = Form(...),  # 1 for upvote, -1 for downvote
    db: Session = Depends(get_db)
):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.post_id == post_id
    ).first()
    
    if existing_vote:
        # Update existing vote
        if existing_vote.vote_type == vote_type:
            # Remove vote
            db.delete(existing_vote)
            post.points -= existing_vote.vote_type
        else:
            # Change vote
            post.points -= existing_vote.vote_type
            existing_vote.vote_type = vote_type
            post.points += vote_type
    else:
        # Create new vote
        new_vote = Vote(
            user_id=current_user.id,
            post_id=post_id,
            vote_type=vote_type
        )
        db.add(new_vote)
        post.points += vote_type
    
    db.commit()
    
    return RedirectResponse(url=request.headers.get("referer", "/"), status_code=302)

@router.post("/favorite/{post_id}")
async def toggle_favorite(
    request: Request,
    post_id: str,
    db: Session = Depends(get_db)
):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already favorited
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.post_id == post_id
    ).first()
    
    if existing_favorite:
        # Remove favorite
        db.delete(existing_favorite)
        is_favorited = False
    else:
        # Add favorite
        new_favorite = Favorite(
            user_id=current_user.id,
            post_id=post_id
        )
        db.add(new_favorite)
        is_favorited = True
    
    db.commit()
    
    return RedirectResponse(url=request.headers.get("referer", "/"), status_code=302) 