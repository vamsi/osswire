from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Comment, Post, User, Vote
from auth import get_current_user
from datetime import datetime
from typing import Optional
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    return get_current_user(db, token)

@router.post("/comment/{post_id}")
async def add_comment(
    request: Request,
    post_id: str,
    content: str = Form(...),
    parent_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not content.strip():
        return RedirectResponse(url=f"/post/{post_id}", status_code=302)
    
    # If this is a reply, verify parent comment exists
    if parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == parent_id).first()
        if not parent_comment or parent_comment.submission_id != post_id:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    new_comment = Comment(
        submission_id=post_id,
        parent_id=parent_id,
        content=content.strip(),
        created_by=current_user.id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return RedirectResponse(url=f"/post/{post_id}", status_code=302)

@router.post("/vote/comment/{comment_id}")
async def vote_comment(
    request: Request,
    comment_id: str,
    vote_type: int = Form(...),  # 1 for upvote, -1 for downvote
    db: Session = Depends(get_db)
):
    current_user = get_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.comment_id == comment_id
    ).first()
    
    if existing_vote:
        # Update existing vote
        if existing_vote.vote_type == vote_type:
            # Remove vote
            db.delete(existing_vote)
            comment.points -= existing_vote.vote_type
        else:
            # Change vote
            comment.points -= existing_vote.vote_type
            existing_vote.vote_type = vote_type
            comment.points += vote_type
    else:
        # Create new vote
        new_vote = Vote(
            user_id=current_user.id,
            comment_id=comment_id,
            vote_type=vote_type
        )
        db.add(new_vote)
        comment.points += vote_type
    
    db.commit()
    
    return RedirectResponse(url=request.headers.get("referer", "/"), status_code=302)

def build_comment_tree(comments, parent_id=None):
    """Build a tree structure from flat comments list"""
    tree = []
    for comment in comments:
        if comment.parent_id == parent_id:
            comment.children = build_comment_tree(comments, comment.id)
            tree.append(comment)
    return tree 