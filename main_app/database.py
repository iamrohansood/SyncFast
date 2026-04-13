from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLite_Database_Path = 'sqlite:///./database.db'

engine = create_engine(SQLite_Database_Path, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
