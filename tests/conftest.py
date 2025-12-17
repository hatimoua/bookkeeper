import pytest
import sys
import os

# 1. Add 'src' to the Python path so we can import modules easily
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm_models import Base
from config import settings
import database 

# Define the connection to the fake in-memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """
    1. Overrides the database engine to use RAM.
    2. Creates all tables.
    3. Yields a session.
    4. Destroys tables after test.
    """
    # --- SETUP ---
    # Create a new engine for the test (In-Memory)
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create the tables in RAM
    Base.metadata.create_all(bind=test_engine)
    
    # Create a session factory bound to this RAM engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # MAGIC: We overwrite the 'SessionLocal' in the real database module
    # Now, when insert_account() calls SessionLocal(), it gets OUR fake one!
    original_session_maker = database.SessionLocal
    database.SessionLocal = TestingSessionLocal
    
    # Create a session for the test to use
    session = TestingSessionLocal()
    
    yield session
    
    # --- TEARDOWN ---
    session.close()
    Base.metadata.drop_all(bind=test_engine)
    
    # Restore the real engine so we don't break anything else
    database.SessionLocal = original_session_maker