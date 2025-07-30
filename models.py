from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from datetime import datetime

Base = declarative_base()

class LicenseType(enum.Enum):
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    GPL_3_0 = "GPL-3.0"
    BSD_3 = "BSD-3"
    ISC = "ISC"
    UNLICENSE = "Unlicense"
    CC0 = "CC0"
    CC_BY_4_0 = "CC-BY-4.0"
    CC_BY_SA_4_0 = "CC-BY-SA-4.0"

class CategoryType(enum.Enum):
    WEB_FRAMEWORK = "Web Framework"
    DATABASE = "Database"
    PROGRAMMING_LANGUAGE = "Programming Language"
    TOOL = "Tool"
    LIBRARY = "Library"
    OPERATING_SYSTEM = "Operating System"
    MACHINE_LEARNING = "Machine Learning"
    DEVOPS = "DevOps"
    MOBILE = "Mobile"
    DESKTOP = "Desktop"
    GAME = "Game"
    SECURITY = "Security"
    NETWORKING = "Networking"
    CLOUD = "Cloud"
    BLOCKCHAIN = "Blockchain"
    OTHER = "Other"

class LanguageType(enum.Enum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    RUST = "Rust"
    GO = "Go"
    JAVA = "Java"
    C_PLUS_PLUS = "C++"
    C_SHARP = "C#"
    PHP = "PHP"
    RUBY = "Ruby"
    SWIFT = "Swift"
    KOTLIN = "Kotlin"
    DART = "Dart"
    SCALA = "Scala"
    ELIXIR = "Elixir"
    HASKELL = "Haskell"
    R = "R"
    MATLAB = "MATLAB"
    SHELL = "Shell"
    HTML_CSS = "HTML/CSS"
    OTHER = "Other"

class SubmissionType(enum.Enum):
    SHOW = "Show"
    LAUNCH = "Launch"
    ASK = "Ask"
    TELL = "Tell"
    NEWS = "News"
    TUTORIAL = "Tutorial"
    RESOURCE = "Resource"
    TOOL = "Tool"
    LIBRARY = "Library"
    FRAMEWORK = "Framework"
    OTHER = "Other"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    oauth_provider = Column(String(20), nullable=True)  # 'google', 'github', or None
    oauth_id = Column(String(100), nullable=True)  # OAuth provider's user ID
    avatar_url = Column(String(500), nullable=True)  # Profile picture URL
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    favorites = relationship("Favorite", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    license = Column(Enum(LicenseType), nullable=True)  # Made optional
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    points = Column(Integer, default=0)
    
    # Thumbnail fields
    thumbnail_url = Column(String(500), nullable=True)
    thumbnail_type = Column(String(50), nullable=True)  # 'image', 'video', 'document', 'website', 'default'
    domain = Column(String(100), nullable=True)
    
    # Tag fields
    category = Column(Enum(CategoryType), nullable=True)
    language = Column(Enum(LanguageType), nullable=True)
    submission_type = Column(Enum(SubmissionType), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    points = Column(Integer, default=0)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    post_id = Column(String, ForeignKey("posts.id"), nullable=True)
    comment_id = Column(String, ForeignKey("comments.id"), nullable=True)
    vote_type = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = Column(DateTime, default=func.now())

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites") 