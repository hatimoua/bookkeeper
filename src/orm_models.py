from sqlalchemy import create_engine, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



# 2. Create the Base Class
# (We will explain this in the next step, but we need it here)
#This is the "Base" class that all our future models (Account, Invoice) will inherit from. 
# It's how SQLAlchemy knows which Python classes map to database tables.
class Base(DeclarativeBase):
    pass

class AccountModel(Base):
    __tablename__ = 'accounts' #This is the actual name is the DB
    
    #the primary Key is the unique ID for each row
    #Since 'code' is unique for each account, we use that as the primary key
    account_name: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String, primary_key=True)    
    financial_stat: Mapped[str] = mapped_column(String)
    group_name: Mapped[str] = mapped_column(String)
    normally: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    
    
class AccountEmbedding(Base):
    __tablename__ = 'account_embeddings'
    
    code: Mapped[str] = mapped_column(String, primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(JSON)  # Store as JSON string    