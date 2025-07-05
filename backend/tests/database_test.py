# backend/app/database_test.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base # Use the same models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Use an in-memory SQLite DB for tests

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    A dependency override to use the test database instead of the real one.
    """
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()
            
def create_test_database():
    """
    Create the test database tables.
    This should be called before running tests.
    """
    Base.metadata.create_all(bind=engine)