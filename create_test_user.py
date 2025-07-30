from database import engine, Base
from models import User
from auth import get_password_hash
from sqlalchemy.orm import sessionmaker

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Create a test user with proper password hash
test_user = User(
    id="test_user_1",
    username="testuser",
    email="test@example.com",
    password_hash=get_password_hash("password123")
)

# Check if user already exists
existing_user = db.query(User).filter(User.username == "testuser").first()
if existing_user:
    print("Test user already exists!")
else:
    db.add(test_user)
    db.commit()
    print("Test user created successfully!")
    print("Username: testuser")
    print("Password: password123")

db.close() 