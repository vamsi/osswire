from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, submissions, comments, oauth, settings
from database import get_db
from sqlalchemy.orm import Session
from auth import get_current_user
from routes.comments import build_comment_tree
from models import Post, Comment

app = FastAPI(title="OSSWire", description="Open Source Software News and Discussion")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(submissions.router, tags=["submissions"])
app.include_router(comments.router, tags=["comments"])
app.include_router(oauth.router, tags=["oauth"])
app.include_router(settings.router, tags=["settings"])

# Dependency to add current user to request state
@app.middleware("http")
async def add_current_user(request: Request, call_next):
    # Get database session
    db = next(get_db())
    try:
        # Get current user from cookie
        token = request.cookies.get("access_token")
        if token:
            current_user = get_current_user(db, token)
            request.state.current_user = current_user
        else:
            request.state.current_user = None
        
        # For post views, build comment tree
        if request.url.path.startswith("/post/"):
            post_id = request.url.path.split("/")[-1]
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                # Build comment tree
                comments = db.query(Comment).filter(Comment.submission_id == post_id).all()
                post.comments = build_comment_tree(comments)
                request.state.post = post
        
        response = await call_next(request)
        return response
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to OSSWire - Open Source Software News and Discussion"}

@app.get("/profile/{username}")
async def profile_main(request: Request, username: str, db: Session = Depends(get_db)):
    from models import User, Post, Comment
    from fastapi.templating import Jinja2Templates
    
    templates = Jinja2Templates(directory="templates")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    submissions = db.query(Post).filter(Post.created_by == user.id).order_by(Post.created_at.desc()).all()
    comments = db.query(Comment).filter(Comment.created_by == user.id).order_by(Comment.created_at.desc()).all()
    
    # Load comments for each submission
    for post in submissions:
        post.comments = db.query(Comment).filter(Comment.submission_id == post.id).all()
        post.author = user
    
    # For now, favorites will be empty (we'll implement this later)
    favorites = []
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": user,
        "submissions": submissions,
        "comments": comments,
        "favorites": favorites
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 