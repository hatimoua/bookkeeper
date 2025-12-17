from sqlalchemy import create_engine, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from orm_models import Base

# 1. Create the Engine
# The string "sqlite:///bookkeeper.db" tells it:
# - Use SQLite driver
# - Create/Open a file named 'bookkeeper.db' in this directory
#sqlite:///bookkeeper.db: This is the Connection String. If we ever switch 
# to Postgres later, we only change this string (e.g., postgresql://user:pass@localhost/db).

engine = create_engine("sqlite:///bookkeeper.db", echo=True)





# 3. Create tables
# This looks at all classes that inherit from 'Base' and creates them in the DB
Base.metadata.create_all(engine)  #This creates the tables in the DB if they don't exist yet