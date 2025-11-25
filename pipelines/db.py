# pipeline/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

ENGINE_URL = "sqlite:///legislation.db"

engine = create_engine(ENGINE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(engine)
