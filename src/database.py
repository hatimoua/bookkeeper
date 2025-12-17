from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from orm_models import Base, AccountModel, AccountEmbedding
from models import Account
from config import settings
from typing import Optional

# 1. Setup the Engine (The Connection)
# check_same_thread=False is needed only for SQLite if multiple parts of the app 
# try to access the DB at once (like a web server). Good practice to have.

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# 2. Setup the Session Factory
# This is a factory that produces new Session objects when we ask for them.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Helper to create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def insert_account(account: AccountModel):
    """
    Take a Pydantic Account object, convert it to ORM model, 
        and save it to the database.
    """
    
    with SessionLocal() as session:
        # Convert Pydantic model to Python dict
        data = account.model_dump()
        
        # Create the ORM object (unpacking the dict)
        db_account = AccountModel(**data)
        
        # Merge checks the Primary Key (code). 
        # If it exists, it updates. If not, it inserts.
        session.merge(db_account)  
        
        # Commit the transaction to save changes
        session.commit()
        
    
def clear_database():
    """Helper to clear all data from the database tables."""
    with SessionLocal() as session:
        session.query(AccountModel).delete()
        session.query(AccountEmbedding).delete()
        session.commit()
        


def insert_account_embedding(code: str, embedding: list[float]):
    """
    Save the vector embedding for a specific account code.
    
    This replaces the JSON serialization logic. SQLAlchemy handles the list-to-JSON conversion.
    """
    
    with SessionLocal() as session:
        #Create the ORM object
        #We just pass the raw list [0.1, 0.2,...] and SQLAlchemy converts it to JSON
        embedding_obj = AccountEmbedding(code=code, embedding=embedding)

        session.merge(embedding_obj)  # Insert or update based on primary key
        session.commit()
        
def load_all_account_embeddings() -> list[tuple[str, list[float]]]:
    """
    Downloads all the vectors from the database so we can do math on them.
    Return a list of (code, embedding_vector) tuples to match the search engine's requirements.   
    """
    
    with SessionLocal() as session:
        #Get all rows from the account_embeddings table
        results = session.query(AccountEmbedding).all()
        
        # Convert ORM objects into the list of tuples the app expects
        # We return [(row.code, row.embedding), ...]
        return [(row.code, row.embedding) for row in results]
    
def get_all_accounts() -> list[Account]: # Notice return type is Pydantic Account
    """Fetch all accounts and convert them to Pydantic models."""
    with SessionLocal() as session:
        # 1. Get ORM objects from DB
        orm_accounts = session.query(AccountModel).all()
        
        #2. Convert each ORM object to Pydantic model/object
        pydantic_accounts = []
        for row in orm_accounts:
            #We map the columns to the Pydantic fields 
            acc = Account(
                code=row.code,
                account_name=row.account_name,
                financial_stat=row.financial_stat,
                group_name=row.group_name,
                normally=row.normally,
                description=row.description 
            )
            pydantic_accounts.append(acc)
        return pydantic_accounts
    

def get_account_by_code(code: str) -> Account | None:
    """Fetch account by its unique code and convert to Pydantic model."""

    with SessionLocal() as session:
        # 1. Query the ORM object by primary key (code)
        orm_account = session.query(AccountModel).filter(AccountModel.code == code).first()
        
        if orm_account is None:
            return None  # Not found
        
        # 2. Convert to Pydantic model
        return Account(
            account_name=orm_account.account_name,
            code=orm_account.code,
            financial_stat=orm_account.financial_stat,
            group_name=orm_account.group_name,              
            normally=orm_account.normally,
            description=orm_account.description
        )

    