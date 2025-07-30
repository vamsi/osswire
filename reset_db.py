import os
from database import SessionLocal
from models import Base
from sqlalchemy import text

def reset_database():
    """Completely reset the database and reseed it"""
    
    # Remove the database file if it exists
    if os.path.exists("osswire.db"):
        os.remove("osswire.db")
        print("Removed existing database file.")
    
    # Create new database and tables
    from database import engine
    Base.metadata.create_all(bind=engine)
    print("Created new database with tables.")
    
    # Run the seed script
    print("Seeding database with fresh data...")
    from seed import seed_database
    seed_database()
    
    print("Database reset completed successfully!")

if __name__ == "__main__":
    reset_database() 